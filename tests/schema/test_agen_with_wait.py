import asyncio
from random import random, randint

import pytest

from typing import AsyncGenerator, Iterable, List, Set

from .funcs import agen_with_wait


async def aiterable(iterable: Iterable) -> AsyncGenerator:
    '''Wrap iterable so can be used with "async for"'''
    for i in iterable:
        await asyncio.sleep(0.01)
        yield i


@pytest.mark.asyncio
async def test_one():
    async def afunc():
        delay = random() * 0.01
        await asyncio.sleep(delay)

    all: Set[asyncio.Task] = set()
    done: List[asyncio.Task] = []

    agen = agen_with_wait(aiterable(range(5)))
    async for i in agen:
        tasks = {asyncio.create_task(afunc()) for _ in range(randint(0, 2))}
        all |= tasks
        done_, pending = await agen.asend(tasks)
        done.extend(done_)

    await asyncio.gather(*pending)
    assert len(all) == len(done) + len(pending)
    assert all == set(done) | set(pending)


@pytest.mark.asyncio
async def test_raise():
    async def agen():
        yield 0
        await asyncio.sleep(0.1)
        assert False  # The line shouldn't be reached

    async def afunc():
        await asyncio.sleep(0)
        raise Exception("foo", "bar")

    obj = agen_with_wait(agen())
    with pytest.raises(Exception) as exc:
        async for i in obj:
            tasks = {asyncio.create_task(afunc())}
            _, pending = await obj.asend(tasks)

    assert ("foo", "bar") == exc.value.args
