__all__ = ['Plugin']

from typing import Mapping, MutableMapping

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
        self._nextline = context['nextline']
        async with self._nextline:
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['nextline'] = self._nextline
