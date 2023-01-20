'''Hook specification for Nextline GraphQL plugin.'''
from typing import Mapping, Optional, Tuple, Union

from nextline import Nextline
from starlette.applications import Starlette

from nextlinegraphql import apluggy
from nextlinegraphql.custom.decorator import asynccontextmanager

hookspec = apluggy.HookspecMarker('nextline')
hookimpl = apluggy.HookimplMarker('nextline')


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
async def lifespan(app: Starlette, nextline: Nextline):
    '''Starlette lifespan'''
    pass


@hookspec
async def get_context(context: Mapping) -> Optional[Mapping]:
    '''Strawberry GraphQL context'''
    pass
