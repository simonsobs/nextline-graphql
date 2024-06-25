from collections.abc import AsyncIterator

from nextline import Nextline
from nextline.events import OnWriteStdout
from nextline.plugin.spec import hookimpl


class CacheStdout:
    def __init__(self, nextline: Nextline) -> None:
        self._nextline = nextline
        self._cache = list[str]()

    async def subscribe(self) -> AsyncIterator[str]:
        yield ''.join(self._cache)
        async for i in self._nextline.subscribe_stdout():
            assert i.text is not None
            yield i.text

    @hookimpl
    async def on_initialize_run(self) -> None:
        self._cache.clear()

    @hookimpl
    async def on_write_stdout(self, event: OnWriteStdout) -> None:
        self._cache.append(event.text)
