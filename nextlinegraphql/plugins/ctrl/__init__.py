__all__ = ['Plugin']

from typing import Mapping

from starlette.applications import Starlette

from nextlinegraphql.custom.decorator import asynccontextmanager
from nextlinegraphql.hook import spec

from .schema import Mutation, Query, Subscription


class Plugin:
    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

    @spec.hookimpl(trylast=True)  # trylast so to be the innermost context
    @asynccontextmanager
    async def lifespan(self, app: Starlette, context: Mapping):
        '''Yield within the nextline context.'''
        nextline = context['nextline']
        async with nextline:
            yield
