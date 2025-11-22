from collections.abc import AsyncIterator
from typing import Any

from nextline.events import OnWriteStdout
from nextline.plugin.spec import hookimpl
from nextline.utils.pubsub import PubSubItem


class CacheStdout:
    def __init__(self) -> None:
        self._pubsub = PubSubItem[str](cache=True)

    async def subscribe(self) -> AsyncIterator[str]:
        async for text in self._pubsub.subscribe():
            yield text

    async def aclose(self) -> None:
        await self._pubsub.aclose()

    async def __aenter__(self) -> 'CacheStdout':
        return self

    async def __aexit__(self, *_: Any, **__: Any) -> None:
        await self.aclose()

    @hookimpl
    async def on_initialize_run(self) -> None:
        self._pubsub.clear()

    @hookimpl
    async def on_write_stdout(self, event: OnWriteStdout) -> None:
        await self._pubsub.publish(event.text)
