__all__ = ['Plugin']

import asyncio
from typing import Mapping, MutableMapping

from apluggy import asynccontextmanager
from nextline import Nextline

from nextlinegraphql.hook import spec

from .schema import Mutation, Query, Subscription
from .types import ContinuousInfo


class Plugin:
    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

    @spec.hookimpl()
    @asynccontextmanager
    async def lifespan(self, context: Mapping):
        nextline: Nextline = context['nextline']
        self._info = ContinuousInfo()
        await self._info.pubsub_enabled.publish(False)
        task = asyncio.create_task(monitor_state(nextline, self._info))
        try:
            yield
        finally:
            await task
            if self._info.tasks:
                await asyncio.gather(*self._info.tasks)

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping) -> None:
        context['continuous_info'] = self._info


async def monitor_state(nextline: Nextline, info: ContinuousInfo):
    tasks = info.tasks
    async for state in nextline.subscribe_state():
        if state == 'initialized' and tasks:
            _, pending = await asyncio.wait(
                tasks, timeout=0.001, return_when=asyncio.FIRST_COMPLETED
            )
            tasks.clear()
            tasks.update(pending)
