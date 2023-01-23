import contextlib
from typing import Optional

from dynaconf import Dynaconf
from nextline import Nextline
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import graphql
from .config import load_settings
from .custom.pluggy import PluginManager
from .example_script import statement
from .hook import initialize_plugins
from .logging import configure_logging


def configure(hook: PluginManager, config: Optional[Dynaconf]) -> None:
    config = config or load_settings(hook)
    hook.hook.configure(settings=config)
    configure_logging(config.logging)


def create_app(config: Optional[Dynaconf] = None, nextline: Optional[Nextline] = None):

    hook = initialize_plugins()

    configure(hook=hook, config=config)

    run_no: int = max(hook.hook.initial_run_no(), default=1)
    script: str = [*hook.hook.initial_script(), statement][0]

    if not nextline:
        nextline = Nextline(script, run_no)

    app_ = graphql.create_app(nextline=nextline, hook=hook)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        assert nextline

        app.mount('/', app_)

        context = {'nextline': nextline}
        hook.hook.update_lifespan_context(app=app, context=context)

        async with hook.awith.lifespan(app=app, context=context):
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
