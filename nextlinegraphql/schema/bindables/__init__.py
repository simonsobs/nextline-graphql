from pathlib import Path
import asyncio
import threading
import traceback
import janus
from ariadne import QueryType, MutationType, SubscriptionType

from nextline import Nextline

from ... import db

##__________________________________________________________________||
query = QueryType()


@query.field("hello")
async def resolve_hello(_, info):
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent


@query.field("helloDb")
async def resolve_hello_db(_, info):
    with db.Session.begin() as session:
        model = session.query(db.models.Hello).one_or_none()
        if model is None:
            return None
        return model.message


@query.field("globalState")
async def resolve_global_state(_, info):
    nextline = get_nextline()
    return nextline.global_state


@query.field("source")
async def resolve_source(_, info, fileName=None):
    nextline = get_nextline()
    return nextline.get_source(fileName)


@query.field("sourceLine")
async def resolve_source_line(_, info, lineNo, fileName=None):
    nextline = get_nextline()
    return nextline.get_source_line(lineNo, fileName)


@query.field("exception")
async def resolve_exception(_, info):
    nextline = get_nextline()
    exc = nextline.exception()
    if not exc:
        return
    ret = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    return ret


##__________________________________________________________________||
subscription = SubscriptionType()


@subscription.source("counter")
async def counter_generator(obj, info):
    for i in range(5):
        await asyncio.sleep(1)
        yield i


@subscription.field("counter")
def counter_resolver(count, info):
    return count + 1


@subscription.source("globalState")
async def global_state_generator(_, info):
    nextline = get_nextline()
    async for s in nextline.subscribe_global_state():
        # if s == 'finished':
        #     print('finished', nextline.exception())
        #     nextline.result()
        yield s


@subscription.field("globalState")
def global_state_resolver(global_state, info):
    return global_state


@subscription.source("threadTaskIds")
async def thread_task_ids_generator(_, info):
    nextline = get_nextline()
    async for y in nextline.subscribe_thread_asynctask_ids():
        yield [{"threadId": e[0], "taskId": e[1]} for e in y]


@subscription.field("threadTaskIds")
def thread_task_ids_resolver(obj, info):
    return obj


@subscription.source("threadTaskState")
async def thread_task_state_generator(_, info, threadId, taskId):
    threadId = int(threadId)
    taskId = int(taskId) if taskId else None
    thread_asynctask_id = (threadId, taskId)
    nextline = get_nextline()
    async for y in nextline.subscribe_thread_asynctask_state(
        thread_asynctask_id
    ):
        # if y['prompting'] and y['trace_event'] == 'return':
        #     nextline.send_pdb_command(thread_asynctask_id, 'return')
        #     continue
        y = {
            "prompting": y["prompting"],
            "fileName": y["file_name"],
            "lineNo": y["line_no"],
            "traceEvent": y["trace_event"],
        }
        yield y


@subscription.field("threadTaskState")
def thread_task_state_resolver(obj, info, threadId, taskId):
    return obj


@subscription.source("stdout")
async def stdout_generator(_, info):
    stdout_queue = await get_stdout_queue()
    queue = stdout_queue.subscribe()
    nextline = get_nextline()
    while True:
        v = await queue.async_q.get()
        if nextline.global_state == "running":
            yield v
    await stdout_queue.unsubscribe(queue)


@subscription.field("stdout")
def stdout_resolver(stdout, info):
    return stdout


##__________________________________________________________________||
mutation = MutationType()


@mutation.field("exec")
async def resolve_exec(_, info):
    # print(_)
    # print(info)
    await run_nextline()
    return True


@mutation.field("reset")
async def resolve_reset(_, info, statement=None):
    reset_nextline(statement=statement)
    return True


@mutation.field("close")
async def resolve_close(_, info):
    await close_nextline()
    return True


@mutation.field("sendPdbCommand")
async def resolve_send_pdb_command(_, info, threadId, taskId, command):
    threadId = int(threadId)
    taskId = int(taskId) if taskId else None
    thread_asynctask_id = (threadId, taskId)
    nextline = get_nextline()
    nextline.send_pdb_command(thread_asynctask_id, command)
    return True


@mutation.field("updateHelloDbMessage")
async def resolve_update_hello_db_message(_, info, message):
    with db.Session.begin() as session:
        model = session.query(db.models.Hello).one_or_none()
        if model is None:
            model = db.models.Hello(message=message)
            session.add(model)
        else:
            model.message = message
        session.commit()
    return True


##__________________________________________________________________||
class StreamOut:
    def __init__(self, queue):
        self.queue = queue

    def write(self, s):
        self.queue.put(s)

    def flush(self):
        pass


class QueueDist:
    def __init__(self, queue: janus.Queue):
        self.queue = queue
        self.subscribers = []

        self.t = threading.Thread(target=self._listen, daemon=True)
        self.t.start()

    def _listen(self):
        while True:
            v = self.queue.sync_q.get()
            for s in self.subscribers:
                s.sync_q.put(v)

    def subscribe(self):
        ret = janus.Queue()
        self.subscribers.append(ret)
        return ret

    async def unsubscribe(self, queue):
        self.subscribers.remove(queue)
        queue.close()
        await queue.wait_closed()


class StdoutQueue:
    def __init__(self, queue: janus.Queue):
        self.queue = queue
        self.stdout_org = sys.stdout
        sys.stdout = StreamOut(self.queue.sync_q)
        self.queue_dist = QueueDist(self.queue)

        self.q = self.subscribe()
        self.t = threading.Thread(target=self._listen, daemon=True)
        self.t.start()

    def _listen(self):
        while True:
            v = self.q.sync_q.get()
            self.stdout_org.write(v)

    def subscribe(self):
        return self.queue_dist.subscribe()

    async def unsubscribe(self, queue):
        await self.queue_dist.unsubscribe(queue)


stdout_queue_holder = []


async def get_stdout_queue():
    if not stdout_queue_holder:
        queue = janus.Queue()
        stdout_queue_holder.append(StdoutQueue(queue))
    return stdout_queue_holder[0]


##__________________________________________________________________||
import sys  # noqa: E402

_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))
del _THIS_DIR

statement = """
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
""".strip()

nextline_holder = []


def get_nextline():
    if not nextline_holder:
        nextline_holder.append(Nextline(statement))
    return nextline_holder[0]


def pop_nextline():
    nextline = get_nextline()
    nextline_holder.clear()
    return nextline


async def run_nextline():
    nextline = get_nextline()
    # print(nextline.global_state)
    if nextline.global_state == "initialized":
        nextline.run()
        asyncio.create_task(_wait(nextline))
    return


async def _wait(nextline):
    await nextline.finish()


def reset_nextline(statement=None):
    nextline = get_nextline()
    nextline.reset(statement=statement)


async def close_nextline():
    nextline = pop_nextline()
    await nextline.close()


##__________________________________________________________________||
bindables = [query, mutation, subscription]

##__________________________________________________________________||
