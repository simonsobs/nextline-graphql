from decorator import contextmanager

from nextlinegraphql.custom import pluggy
from nextlinegraphql.custom.decorator import asynccontextmanager

hookspec = pluggy.HookspecMarker('myproject')
hookimpl = pluggy.HookimplMarker('myproject')


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
