'''Hook specification for Nextline GraphQL plugin.'''
from typing import MutableMapping, Optional, Sequence, Tuple, Union

from dynaconf import Dynaconf, Validator
from starlette.applications import Starlette

from nextlinegraphql.custom import pluggy
from nextlinegraphql.custom.decorator import asynccontextmanager

PROJECT_NAME = 'nextline'

hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


@hookspec
def dynaconf_preload() -> Optional[Sequence[str]]:
    '''Return settings file paths of the plugin to be preloaded.

    The paths will be included in the "preload" option of Dynaconf.

    https://www.dynaconf.com/configuration/#preload
    '''
    pass


@hookspec
def dynaconf_settings_files() -> Optional[Sequence[str]]:
    '''Return settings file paths of the plugin.

    The paths will be included in the "settings_files" option of Dynaconf.

    https://www.dynaconf.com/configuration/#settings_file-or-settings_files
    '''
    pass


@hookspec
def dynaconf_validators() -> Optional[Sequence[Validator]]:
    '''Return validators of the plugin settings.

    The validators will be included in the "validators" option of Dynaconf.

    https://www.dynaconf.com/configuration/#validators
    '''
    pass


@hookspec
def configure(settings: Dynaconf, hook: pluggy.PluginManager) -> None:
    '''Initialize the plugin.'''
    pass


@hookspec
def initial_run_no() -> Optional[int]:
    '''Run No. of the first run.'''
    pass


@hookspec
def initial_script() -> Optional[str]:
    '''The script of the first run.'''
    pass


@hookspec
def schema() -> Optional[Tuple[type, Union[type, None], Union[type, None]]]:
    '''The GraphQL schema (Query, Mutation, Subscription)'''
    pass


@hookspec
def update_lifespan_context(
    app: Starlette, hook: pluggy.PluginManager, context: MutableMapping
) -> None:
    '''Called within the Starlette lifespan context before the lifespan hook.

    The context is passed to the lifespan hook.
    '''


@hookspec
@asynccontextmanager
async def lifespan(app: Starlette, hook: pluggy.PluginManager, context: MutableMapping):
    '''Called within the Starlette lifespan context.

    The context is passed from the update_lifespan_context hook.

    The Starlette lifespan yields within this hook
    '''
    pass


@hookspec
def update_strawberry_context(context: MutableMapping) -> None:
    '''Called within get_context() of a subclass of strawberry.asgi.GraphQL.

    Plugins can modify the context in place.

    Strawberry Doc: https://strawberry.rocks/docs/integrations/asgi#get_context
    '''
    pass
