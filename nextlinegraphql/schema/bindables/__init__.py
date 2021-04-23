from collections import deque
from pathlib import Path
import asyncio
import threading
import janus
from ariadne import QueryType, MutationType, SubscriptionType, ObjectType

from nextline import Nextline

##__________________________________________________________________||
query = QueryType()
subscription = SubscriptionType()
mutation = MutationType()

@query.field("hello")
async def resolve_hello(_, info):
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent

@query.field("state")
async def resolve_state(_, info):
    nextline = get_nextline()
    return nextline

state = ObjectType("State")

@state.field("state")
async def resolve_state_state(nextline, *_):
    return nextline.status

@state.field("nthreads")
async def resolve_state_nthreads(nextline, *_):
    return nextline.nthreads()

@state.field("threads")
async def resolve_state_threads(nextline, *_):
    return reshape_state(nextline.state)

def reshape_state(state):
    if state is None:
        return []
    state = state.data
    ret = [
        {
            "threadId": str(thid),
            "tasks": [
                {
                    "taskId": str(taid) if taid else "",
                    "prompting": tada['prompting'],
                    "fileName": tada['file_name'],
                    "lineNo": tada['line_no'],
                    "fileLines": tada['file_lines']
                } for taid, tada in thda.items()
            ]
        } for thid, thda in state.items()
    ]
    return ret

@subscription.source("state")
async def state_generator(obj, info):
    nextline = get_nextline()
    async for n in nextline.nextline_generator():
        yield n

@subscription.field("state")
async def state_resolver(state, info):
    return state

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

@subscription.source("stdout")
async def stdout_generator(_, info):
    stdout_queue = await get_stdout_queue()
    queue = stdout_queue.subscribe()
    nextline = get_nextline()
    while True:
        v = await queue.async_q.get()
        if nextline.status == 'running':
            yield v
    await stdout_queue.unsubscribe(queue)

@subscription.field("stdout")
async def stdout_resolver(stdout, info):
    return stdout

@subscription.source("counter")
async def counter_generator(obj, info):
    for i in range(5):
        await asyncio.sleep(1)
        yield i

@subscription.field("counter")
def counter_resolver(count, info):
    return count + 1

##__________________________________________________________________||
import sys
_THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_THIS_DIR))
del _THIS_DIR

statement = """
import time
time.sleep(3)

def f():
    for _ in range(1000):
        pass
    return

f()
f()

import scriptone
scriptone.run()

import scripttwo
scripttwo.run()
""".strip()

breaks = {
    # '__main__': ['<module>'],
    'script': ['run', 'run_threads', 'task', 'task_imp', 'atask', 'run_coroutines']
}

nextline_holder = []

def get_nextline():
    if not nextline_holder:
        nextline_holder.append(Nextline(statement, breaks))
    return nextline_holder[0]

async def run_nextline():
    nextline = get_nextline()
    # print(nextline.status)
    if nextline.status == 'initialized':
        nextline.run()
    return

def reset_nextline():
    nextline_holder[:] = []
    get_nextline()
    event = get_event()
    event.set()

@mutation.field("exec")
async def resolve_exec(_, info):
    # print(_)
    # print(info)
    await run_nextline()
    return True

@mutation.field("reset")
async def resolve_reset(_, info):
    reset_nextline()
    return True

@mutation.field("sendPdbCommand")
async def resolve_send_pdb_command(_, info, threadId, taskId, command):
    threadId = int(threadId)
    taskId = int(taskId) if taskId else None
    thread_asynctask_id = (threadId, taskId)
    nextline = get_nextline()
    pdb_ci = nextline.pdb_ci_registry.get_ci(thread_asynctask_id)
    if pdb_ci is None:
        return False
    pdb_ci.send_pdb_command(command)
    return True

##__________________________________________________________________||
bindables = [query, mutation, subscription, state]

##__________________________________________________________________||
