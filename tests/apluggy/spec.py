from decorator import contextmanager

from nextlinegraphql.custom import apluggy
from nextlinegraphql.custom.decorator import asynccontextmanager

hookspec = apluggy.HookspecMarker('myproject')
hookimpl = apluggy.HookimplMarker('myproject')


@hookspec
def func(arg1, arg2):
    pass


@hookspec
async def afunc(arg1, arg2):
    pass


@hookspec
@contextmanager
def context(arg1, arg2):
    yield


@hookspec
@asynccontextmanager
async def acontext(arg1, arg2):
    yield
