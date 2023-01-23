import contextlib
import logging.config
from typing import Dict

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .config import load_settings
from .hook import load_plugins


def create_app() -> Starlette:
    '''App factory for Uvicorn

    Use the factory option to run.

    $ uvicorn --factory nextlinegraphql:create_app

    Uvicorn Doc: https://www.uvicorn.org/#application-factories
    '''

    hook = load_plugins()
    config = load_settings(hook)
    hook.hook.configure(settings=config, hook=hook)
    configure_logging(config.logging)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
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


def configure_logging(config: Dict):
    logging.config.dictConfig(config)

    # https://pypi.org/project/logging_tree/
    # import logging_tree
    # logging_tree.printout()
