import threading
import asyncio

def task_imp():
    for i in range(2):
        print('in task() i={}'.format(i))

def task():
    task_imp()
    return

def run_threads():
    nthreads = 2
    threads = [ ]
    for i in range(nthreads):
        t = threading.Thread(target=task)
        t.start()
        threads.append(t)
        # time.sleep(0.1)
    for t in threads:
        t.join()

async def atask():
    await asyncio.sleep(1)
    print('here')

async def run_coroutines():
    a1 = asyncio.create_task(atask())
    a2 = asyncio.create_task(atask())
    a3 = asyncio.create_task(atask())
    await asyncio.wait({a1, a2, a3})

def run():
    run_threads()
    asyncio.run(run_coroutines())

if __name__ == '__main__':
    run()

