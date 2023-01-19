from starlette.applications import Starlette

from nextlinegraphql import apluggy
from nextlinegraphql.decorator import asynccontextmanager

hookspec = apluggy.HookspecMarker('nextline')
hookimpl = apluggy.HookimplMarker('nextline')


@hookspec
@asynccontextmanager
def lifespan(app: Starlette):
    pass
