__all__ = ['Plugin']

from typing import AsyncIterator, MutableMapping

from nextline import Nextline

from nextlinegraphql.custom import pluggy
from nextlinegraphql.custom.decorator import asynccontextmanager
from nextlinegraphql.example_script import statement
from nextlinegraphql.hook import spec

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
        context['nextline'] = self._nextline

    @spec.hookimpl(trylast=True)  # trylast so to be the innermost context
    @asynccontextmanager
    async def lifespan(self) -> AsyncIterator[None]:
        '''Yield within the nextline context.'''
        async with self._nextline:
            yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['nextline'] = self._nextline
