import contextlib
from typing import Dict

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from . import graphql
from .config import load_settings
from .hook import load_plugins
from .logging import configure_logging


def create_app() -> Starlette:

    hook = load_plugins()

    config = load_settings(hook)

    hook.hook.configure(settings=config, hook=hook)

    configure_logging(config.logging)

    app_ = graphql.create_app(hook=hook)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):

        app.mount('/', app_)

        context: Dict = {}
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
