import contextlib
import logging.config
from logging import getLogger
from typing import Any

from loguru import logger
from rich import print
from rich.logging import RichHandler
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .config import load_settings
from .hook import load_plugins

logger.configure(
    handlers=[
        {
            "sink": RichHandler(markup=True, log_time_format='[%X]', show_path=False),
            "format": "[dim]\\[{name}:{line}][/dim] {message}",
        }
    ]
)


def create_app() -> Starlette:
    '''App factory for Uvicorn

    Use the factory option to run.

    $ uvicorn --factory nextlinegraphql:create_app

    Uvicorn Doc: https://www.uvicorn.org/#application-factories
    '''

    hook = load_plugins()
    config = load_settings(hook)
    print('Settings:', config.as_dict())

    hook.hook.configure(settings=config, hook=hook)
    configure_logging(config.logging)

    logger = getLogger(__name__)

    plugin_names = [n for n, p in hook.list_name_plugin() if p]
    logger.info(f'Pluggy project name: {hook.project_name!r}')
    logger.info(f'Loaded plugins: {plugin_names}')

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):
        context = dict[Any, Any]()
        await hook.ahook.update_lifespan_context(app=app, hook=hook, context=context)
        async with hook.awith.lifespan(app=app, hook=hook, context=context):
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


def configure_logging(config: dict):
    logging.config.dictConfig(config)

    # https://pypi.org/project/logging_tree/
    # import logging_tree
    # logging_tree.printout()
