import sys
import io
import datetime

from typing import AsyncGenerator, Callable, Tuple, Union, TextIO

from nextline.utils import QueueDist


AGenDatetimeStr = AsyncGenerator[Tuple[datetime.datetime, str], None]


class IOSubscription(io.TextIOWrapper):
    def __init__(self, src: TextIO):
        """Make output stream subscribable

        The src needs to be replaced with the instance of this class. For
        example, if the src is stdout,
            sys.stdout = IOSubscription(sys.stdout)

        NOTE: The code on the logic about the buffer copied from
        https://github.com/alphatwirl/atpbar/blob/894a7e0b4d81aa7b/atpbar/stream.py#L54
        """
        self._queue = QueueDist()
        self._src = src
        self._buffer = ""

    def write(self, s: str) -> int:

        ret = self._src.write(s)
        # TypeError if s isn't str as long as self._src is sys.stdout or
        # sys.stderr.

        self._buffer += s
        if s.endswith("\n"):
            self.flush()
        return ret

    def flush(self):
        if not self._buffer:
            return
        now = datetime.datetime.now()
        self._queue.put((now, self._buffer))
        self._buffer = ""

    async def subscribe(self) -> AGenDatetimeStr:
        async for y in self._queue.subscribe():
            yield y


def create_subscribe_stdout() -> Callable[[], AGenDatetimeStr]:
    stream: Union[IOSubscription, None] = None

    async def subscribe_stdout() -> AGenDatetimeStr:
        nonlocal stream
        if not stream:
            stream = sys.stdout = IOSubscription(sys.stdout)
        async for y in stream.subscribe():
            yield y

    return subscribe_stdout


subscribe_stdout = create_subscribe_stdout()
