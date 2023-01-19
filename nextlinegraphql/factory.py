import contextlib
from typing import Any, Optional

from dynaconf import Dynaconf
from nextline import Nextline
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import apluggy
from . import db
from . import spec
from .config import create_settings
from .example_script import statement
from .logging import configure_logging
from .schema import schema
from .strawberry_fix import GraphQL


class EGraphQL(GraphQL):
    """Extend the strawberry GraphQL app

    https://strawberry.rocks/docs/integrations/asgi
    """

    def __init__(self, nextline: Nextline, pm: apluggy.PluginManager):
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


def create_app(config: Optional[Dynaconf] = None, nextline: Optional[Nextline] = None):

    config = config or create_settings()

    pm = apluggy.PluginManager('nextline')
    pm.add_hookspecs(spec)
    pm.register(db.Plugin(config=config))

    configure_logging(config.logging)

    run_no: int = max(pm.hook.initial_run_no(), default=1)
    script: str = [*pm.hook.initial_script(), statement][0]

    if not nextline:
        nextline = Nextline(script, run_no)

    app_ = EGraphQL(nextline, pm=pm)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        assert nextline

        async with pm.awith.lifespan(app=app, nextline=nextline):
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
    app.mount("/", app_)

    return app
