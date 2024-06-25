from collections.abc import AsyncIterator
from typing import Any

from nextline.events import OnWriteStdout
from nextline.plugin.spec import hookimpl
from nextline.utils.pubsub import PubSubItem


class CacheStdout:
    def __init__(self) -> None:
        self._cache = list[str]()
        self._pubsub = PubSubItem[str]()

    async def subscribe(self) -> AsyncIterator[str]:
        # TODO: Make sure no missing or duplicated items are yielded. If the
        # `last` option is `True`, duplicate items can be yielded and shown on
        # the web client. However, the tests still pass.
        # NOTE: The cache can be implemented in `PubSubItem` itself.
        yield ''.join(self._cache)
        async for text in self._pubsub.subscribe(last=False):
            yield text

    async def aclose(self) -> None:
        await self._pubsub.aclose()

    async def __aenter__(self) -> 'CacheStdout':
        return self

    async def __aexit__(self, *_: Any, **__: Any) -> None:
        await self.aclose()

    @hookimpl
    async def on_initialize_run(self) -> None:
        self._cache.clear()

    @hookimpl
    async def on_write_stdout(self, event: OnWriteStdout) -> None:
        self._cache.append(event.text)
        await self._pubsub.publish(event.text)
