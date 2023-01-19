from starlette.applications import Starlette

from nextlinegraphql.decorator import asynccontextmanager

from . import spec


@spec.hookimpl
@asynccontextmanager
async def lifespan(app: Starlette):
    print('Plugin1.lifespan', app)
    try:
        yield
    finally:
        print('Plugin1.lifespan finally', app)
