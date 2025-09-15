import contextlib
import logging.config
from collections.abc import AsyncIterator
from logging import getLogger
from typing import Any

from apluggy import PluginManager
from dynaconf import LazySettings
from rich import print
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .config import load_settings
from .hook import load_plugins


def create_app(
    enable_external_plugins: bool = True,
    enable_logging_configuration: bool = True,
    print_settings: bool = True,
) -> Starlette:
    '''App factory for Uvicorn.

    Parameters
    ----------
    enable_external_plugins
        Do not load external plugins if False. (Used for tests.)
    enable_logging_configuration
        Leave logging configuration intact if False. (Used for tests.)
    print_settings
        Do not print settings if False. (Used for tests.)

    Returns
    -------
    Starlette
        The configured ASGI application instance.

    Notes
    -----
    Use the factory option to run with Uvicorn:

    $ uvicorn --factory nextlinegraphql:create_app

    See Also
    --------
    Uvicorn Application Factories : https://www.uvicorn.org/#application-factories

    '''

    hook, config = create_hook_and_config(
        enable_external_plugins=enable_external_plugins,
        enable_logging_configuration=enable_logging_configuration,
        print_settings=print_settings,
    )

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        context = dict[Any, Any]()
        await hook.ahook.update_lifespan_context(app=app, hook=hook, context=context)
        async with hook.awith.lifespan(
            app=app, hook=hook, context=context
        ):  # pragma: no branch
            yield

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=config.cors['allow_origins'],
            allow_methods=['GET', 'POST', 'OPTIONS'],
            allow_headers=config.cors['allow_headers'],
            allow_credentials=config.cors['allow_credentials'],
        )
    ]

    app = Starlette(debug=True, lifespan=lifespan, middleware=middleware)

    return app


def create_hook_and_config(
    enable_external_plugins: bool,
    enable_logging_configuration: bool,
    print_settings: bool
) -> tuple[PluginManager, LazySettings]:
    hook = load_plugins(external=enable_external_plugins)
    config = load_settings(hook)
    if print_settings:
        print('Settings:', config.as_dict())

    if enable_logging_configuration:
        configure_logging(config.logging)
    logger = getLogger(__name__)
    logger.info('Logging configured')

    hook.hook.configure(settings=config, hook=hook)

    plugin_names = [n for n, p in hook.list_name_plugin() if p]
    logger.info(f'Pluggy project name: {hook.project_name!r}')
    logger.info(f'Loaded plugins: {plugin_names}')
    return hook, config


def configure_logging(config: dict) -> None:
    logging.config.dictConfig(config)

    # https://pypi.org/project/logging_tree/
    # import logging_tree
    # logging_tree.printout()
