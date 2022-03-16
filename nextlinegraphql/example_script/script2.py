from threading import Thread
import asyncio


def in_thread():
    print("in_thread()")
    asyncio.run(in_task())


async def in_task():
    print("in_task()")


thread = Thread(target=in_thread)
thread.start()
thread.join()

print("here")
