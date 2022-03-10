from threading import Thread


def run():
    t1 = Thread(target=f1)
    t1.start()
    t2 = Thread(target=f2)
    t2.start()
    t2.join()
    t1.join()
    return


def f1():
    for _ in range(5):
        pass
    return


def f2():
    for _ in range(5):
        pass
    return
