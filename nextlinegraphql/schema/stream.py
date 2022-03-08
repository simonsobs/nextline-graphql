import sys
import io

from typing import AsyncGenerator, Callable, Union, TextIO

from nextline.utils import QueueDist


AGenStr = AsyncGenerator[str, None]


class IOSubscription(io.TextIOWrapper):
    def __init__(self, src: TextIO):
        """Make output stream subscribable

        The src needs to be replaced with the instance of this class. For
        example, if the src is stdout,
            sys.stdout = IOSubscription(sys.stdout)
        """
        self._queue = QueueDist()
        self._src = src

    def write(self, s: str) -> int:
        self._queue.put(s)
        return self._src.write(s)

    def flush(self):
        pass

    async def subscribe(self) -> AGenStr:
        async for y in self._queue.subscribe():
            yield y


def create_subscribe_stdout() -> Callable[[], AGenStr]:
    stream: Union[IOSubscription, None] = None

    async def subscribe_stdout() -> AGenStr:
        nonlocal stream
        if not stream:
            stream = sys.stdout = IOSubscription(sys.stdout)
        async for y in stream.subscribe():
            yield y

    return subscribe_stdout


subscribe_stdout = create_subscribe_stdout()
