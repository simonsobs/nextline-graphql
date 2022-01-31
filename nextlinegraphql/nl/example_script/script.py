import time
time.sleep(0.3)

def f():
    for _ in range(10):
        pass
    return

f()
f()

print('here!')

import script_threading
script_threading.run()


import script_asyncio
script_asyncio.run()