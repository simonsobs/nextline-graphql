'''Hook specification for Nextline GraphQL plugin.'''
from collections.abc import AsyncIterator, MutableMapping, Sequence
from typing import Optional

import apluggy as pluggy
from apluggy import asynccontextmanager
from dynaconf import Dynaconf, Validator
from starlette.applications import Starlette

PROJECT_NAME = 'nextline_graphql'

hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


@hookspec
def dynaconf_preload() -> Optional[Sequence[str]]:
    '''Return settings file paths of the plugin to be preloaded.

    The paths will be included in the "preload" option of Dynaconf.

    https://www.dynaconf.com/configuration/#preload
    '''


@hookspec
def dynaconf_settings_files() -> Optional[Sequence[str]]:
    '''Return settings file paths of the plugin.

    The paths will be included in the "settings_files" option of Dynaconf.

    https://www.dynaconf.com/configuration/#settings_file-or-settings_files
    '''


@hookspec
def dynaconf_validators() -> Optional[Sequence[Validator]]:
    '''Return validators of the plugin settings.

    The validators will be included in the "validators" option of Dynaconf.

    https://www.dynaconf.com/configuration/#validators
    '''


@hookspec
def configure(settings: Dynaconf, hook: pluggy.PluginManager) -> None:
    '''Initialize the plugin.'''


@hookspec
def schema() -> Optional[tuple[type, type | None, type | None]]:
    '''The GraphQL schema (Query, Mutation, Subscription)'''


@hookspec
async def update_lifespan_context(
    app: Starlette, hook: pluggy.PluginManager, context: MutableMapping
) -> None:
    '''Update the context object before it is passed to the lifespan hook.'''


@hookspec
@asynccontextmanager
async def lifespan(
    app: Starlette, hook: pluggy.PluginManager, context: MutableMapping
) -> AsyncIterator[None]:
    '''Called within the Starlette lifespan context.

    The context is passed from the update_lifespan_context hook.

    The Starlette lifespan yields within this hook
    '''
    yield


@hookspec
def update_strawberry_context(context: MutableMapping) -> None:
    '''Called within get_context() of a subclass of strawberry.asgi.GraphQL.

    Plugins can modify the context in place.

    Strawberry Doc: https://strawberry.rocks/docs/integrations/asgi#get_context
    '''
