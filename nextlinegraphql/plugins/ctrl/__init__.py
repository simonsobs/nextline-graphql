__all__ = ['Plugin']

from collections.abc import AsyncIterator, MutableMapping

from apluggy import asynccontextmanager
from nextline import Nextline

from nextlinegraphql.hook import spec

from .cache import CacheStdout
from .example_script import statement
from .schema import Mutation, Query, Subscription


class Plugin:
    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    async def update_lifespan_context(self, context: MutableMapping) -> None:
        self._nextline = Nextline(statement)
        self._stdout_cache = list[str]()
        context['nextline'] = self._nextline

    @spec.hookimpl(trylast=True)  # trylast so to be the innermost context
    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        '''Yield within the nextline context.'''
        async with self._nextline:
            self._nextline.register(CacheStdout(self._stdout_cache))
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['nextline'] = self._nextline
        context['stdout_cache'] = self._stdout_cache
