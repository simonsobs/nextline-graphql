import threading
import asyncio

def task_imp():
    tid = threading.get_ident()
    for i in range(2):
        print('in task() i={}'.format(i))

def task():
    return task_imp()

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
    print('here')

async def run_coroutines():
    a1 = atask()
    a2 = atask()
    a3 = atask()
    await asyncio.gather(a1, a2, a3)

def run():
    run_threads()
    asyncio.run(run_coroutines())

if __name__ == '__main__':
    run()

