'''Hook specification for Nextline GraphQL plugin.'''
from typing import Mapping

from nextline import Nextline
from starlette.applications import Starlette

from nextlinegraphql import apluggy
from nextlinegraphql.decorator import asynccontextmanager

hookspec = apluggy.HookspecMarker('nextline')
hookimpl = apluggy.HookimplMarker('nextline')


@hookspec
def initial_run_no():
    pass


@hookspec
def initial_script():
    pass


@hookspec
@asynccontextmanager
async def lifespan(app: Starlette, nextline: Nextline):
    pass


@hookspec
async def get_context(context: Mapping):
    pass
