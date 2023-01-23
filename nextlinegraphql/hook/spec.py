'''Hook specification for Nextline GraphQL plugin.'''
from typing import Mapping, MutableMapping, Optional, Tuple, Union

from dynaconf import Dynaconf, Validator
from starlette.applications import Starlette

from nextlinegraphql.custom import pluggy
from nextlinegraphql.custom.decorator import asynccontextmanager

PROJECT_NAME = 'nextline'

hookspec = pluggy.HookspecMarker(PROJECT_NAME)
hookimpl = pluggy.HookimplMarker(PROJECT_NAME)


@hookspec
def dynaconf_preload() -> Optional[Tuple[str, ...]]:
    '''Default settings file paths of the plugin.'''
    pass


@hookspec
def dynaconf_settings_files() -> Optional[Tuple[str, ...]]:
    '''Settings file paths of the plugin.'''
    pass


@hookspec
def dynaconf_validators() -> Optional[Tuple[Validator, ...]]:
    '''Validators of the plugin settings.'''
    pass


@hookspec
def configure(settings: Dynaconf) -> None:
    '''Initialize the plugin with the settings.'''
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
@asynccontextmanager
async def lifespan(app: Starlette, context: MutableMapping):
    '''Starlette lifespan'''
    pass


@hookspec
async def get_context(context: Mapping) -> Optional[Mapping]:
    '''Strawberry GraphQL context'''
    pass
