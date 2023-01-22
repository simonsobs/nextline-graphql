import contextlib
from itertools import chain
from typing import Any, Optional

import strawberry
from dynaconf import Dynaconf
from nextline import Nextline
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from strawberry.schema import BaseSchema
from strawberry.tools import merge_types

from . import spec
from .config import create_settings
from .custom import pluggy
from .custom.strawberry import GraphQL
from .example_script import statement
from .logging import configure_logging
from .plugins import ctrl, db


def compose_schema(pm: pluggy.PluginManager) -> BaseSchema:

    # [(Query, Mutation, Subscription), ...]
    three_types = pm.hook.schema()

    # [(Query, ...), (Mutation, ...), (Subscription, ...)]
    transposed = list(map(tuple, zip(*three_types)))
    transposed = [tuple(t for t in l if t) for l in transposed]  # remove None

    q, m, s = transposed
    assert q  # Query is required
    Query = merge_types('Query', q)  # type: ignore
    Mutation = m and merge_types('Mutation', m) or None  # type: ignore
    Subscription = s and merge_types('Subscription', s) or None  # type: ignore

    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
    )

    return schema


def configure(pm: pluggy.PluginManager, config: Optional[Dynaconf]) -> None:

    config = config or create_settings(
        preload=tuple(chain(*pm.hook.dynaconf_preload())),
        settings_files=tuple(chain(*pm.hook.dynaconf_settings_files())),
        validators=tuple(chain(*pm.hook.dynaconf_validators())),
    )

    pm.hook.configure(settings=config)
    configure_logging(config.logging)

    # print(config.__dict__)
    # print(config.as_dict())


class EGraphQL(GraphQL):
    """Extend the strawberry GraphQL app

    https://strawberry.rocks/docs/integrations/asgi
    """

    def __init__(
        self,
        schema: BaseSchema,
        nextline: Nextline,
        pm: pluggy.PluginManager,
    ):
        super().__init__(schema)
        self._nextline = nextline
        self._pm = pm

    async def get_context(self, request, response=None) -> Optional[Any]:
        context = {
            "request": request,
            "response": response,
            "nextline": self._nextline,
        }
        updates = await self._pm.ahook.get_context(context=context)
        for update in updates:
            if update:
                context.update(update)
        return context


def initialize_plugins() -> pluggy.PluginManager:
    hook = pluggy.PluginManager(spec.PROJECT_NAME)
    hook.add_hookspecs(spec)
    hook.load_setuptools_entrypoints(spec.PROJECT_NAME)
    hook.register(db.Plugin())
    hook.register(ctrl.Plugin())
    return hook


def create_app(config: Optional[Dynaconf] = None, nextline: Optional[Nextline] = None):

    hook = initialize_plugins()

    configure(pm=hook, config=config)

    run_no: int = max(hook.hook.initial_run_no(), default=1)
    script: str = [*hook.hook.initial_script(), statement][0]

    if not nextline:
        nextline = Nextline(script, run_no)

    schema = compose_schema(pm=hook)
    app_ = EGraphQL(schema=schema, nextline=nextline, pm=hook)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        assert nextline

        app.mount('/', app_)

        async with hook.awith.lifespan(app=app, nextline=nextline):
            async with nextline:
                yield

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    app = Starlette(debug=True, lifespan=lifespan, middleware=middleware)

    return app
