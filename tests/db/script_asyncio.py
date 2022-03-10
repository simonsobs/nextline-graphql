import asyncio


def run():
    asyncio.run(c())
    return


async def c():
    a = asyncio.create_task(d())
    await asyncio.sleep(0.001)
    await asyncio.sleep(0)
    await a
    return


async def d():
    await asyncio.sleep(0)
    await asyncio.sleep(0.001)
    return
