import contextlib
from typing import Any, Optional

import strawberry
from dynaconf import Dynaconf
from nextline import Nextline
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from strawberry.schema import BaseSchema
from strawberry.tools import merge_types

from .config import load_settings
from .custom.pluggy import PluginManager
from .custom.strawberry import GraphQL
from .example_script import statement
from .hook import initialize_plugins
from .logging import configure_logging


def compose_schema(hook: PluginManager) -> BaseSchema:

    # [(Query, Mutation, Subscription), ...]
    three_types = hook.hook.schema()

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


def configure(hook: PluginManager, config: Optional[Dynaconf]) -> None:
    config = config or load_settings(hook)
    hook.hook.configure(settings=config)
    configure_logging(config.logging)


class EGraphQL(GraphQL):
    """Extend the strawberry GraphQL app

    https://strawberry.rocks/docs/integrations/asgi
    """

    def __init__(
        self,
        schema: BaseSchema,
        nextline: Nextline,
        hook: PluginManager,
    ):
        super().__init__(schema)
        self._nextline = nextline
        self._hook = hook

    async def get_context(self, request, response=None) -> Optional[Any]:
        context = {
            "request": request,
            "response": response,
            "nextline": self._nextline,
        }
        updates = await self._hook.ahook.get_context(context=context)
        for update in updates:
            if update:
                context.update(update)
        return context


def create_app(config: Optional[Dynaconf] = None, nextline: Optional[Nextline] = None):

    hook = initialize_plugins()

    configure(hook=hook, config=config)

    run_no: int = max(hook.hook.initial_run_no(), default=1)
    script: str = [*hook.hook.initial_script(), statement][0]

    if not nextline:
        nextline = Nextline(script, run_no)

    schema = compose_schema(hook=hook)
    app_ = EGraphQL(schema=schema, nextline=nextline, hook=hook)

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
