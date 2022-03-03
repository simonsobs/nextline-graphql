import asyncio
from random import random, randint

import pytest

from typing import AsyncGenerator, Iterable

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

    agen = agen_with_wait(aiterable(range(5)))
    async for i in agen:
        tasks = {asyncio.create_task(afunc()) for _ in range(randint(0, 2))}
        _, pending = await agen.asend(tasks)

    await asyncio.gather(*pending)


@pytest.mark.asyncio
async def test_raise():
    all_tasks = asyncio.all_tasks()

    async def afunc():
        raise Exception()

    agen = agen_with_wait(aiterable(range(5)))
    with pytest.raises(Exception):
        async for i in agen:
            tasks = {asyncio.create_task(afunc())}
            _, pending = await agen.asend(tasks)

    await asyncio.gather(*(asyncio.all_tasks() - all_tasks))
    # <Task pending name='Task-21' coro=<<async_generator_asend without __name__>()>
