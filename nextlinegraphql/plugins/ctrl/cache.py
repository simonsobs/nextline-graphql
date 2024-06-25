from nextline.events import OnWriteStdout
from nextline.plugin.spec import hookimpl


class CacheStdout:
    def __init__(self, cache: list[str]) -> None:
        self._cache = cache

    @hookimpl
    async def on_initialize_run(self) -> None:
        self._cache.clear()

    @hookimpl
    async def on_write_stdout(self, event: OnWriteStdout) -> None:
        self._cache.append(event.text)
