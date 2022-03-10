import time

time.sleep(0.001)


def f():
    for _ in range(10):
        pass
    return


f()
f()

print("here!")

import script_threading  # noqa: E402

script_threading.run()  # step

import script_asyncio  # noqa: E402

script_asyncio.run()  # step
