__all__ = ['Plugin']

import asyncio
from collections.abc import AsyncIterator, MutableMapping

import apluggy as pluggy
from apluggy import asynccontextmanager
from nextline import Nextline
from nextline.types import StdoutInfo
from nextline.utils import merge_aiters

from nextlinegraphql.hook import spec

from .example_script import statement
from .schema import Mutation, Query, Subscription


class Plugin:
    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

    @spec.hookimpl
    async def update_lifespan_context(
        self, hook: pluggy.PluginManager, context: MutableMapping
    ) -> None:
        run_no: int = max(hook.hook.initial_run_no(), default=1)
        script: str = [*hook.hook.initial_script(), statement][0]
        self._nextline = Nextline(script, run_no)
        self._stdout_cache = list[str]()
        context['nextline'] = self._nextline

    @spec.hookimpl(trylast=True)  # trylast so to be the innermost context
    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        '''Yield within the nextline context.'''
        async with (self._nextline, self._cache_stdout()):
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['nextline'] = self._nextline
        context['stdout_cache'] = self._stdout_cache

    @asynccontextmanager
    async def _cache_stdout(self) -> AsyncIterator[None]:
        task = asyncio.create_task(self.__cache_stdout())
        try:
            yield
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def __cache_stdout(self) -> None:
        aiters = merge_aiters(
            self._nextline.subscribe_state(), self._nextline.subscribe_stdout()
        )
        async for _, v in aiters:
            match v:
                case 'initialized':
                    self._stdout_cache.clear()
                case StdoutInfo(text=text) if text is not None:
                    self._stdout_cache.append(text)
