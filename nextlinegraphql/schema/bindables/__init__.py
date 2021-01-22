from collections import deque
from pathlib import Path
import asyncio
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
    return { }

state = ObjectType("State")

@state.field("state")
async def resolve_state_state(obj, *_):
    nextline = get_nextline()
    return nextline.status

@state.field("nthreads")
async def resolve_state_nthreads(obj, *_):
    nextline = get_nextline()
    return nextline.nthreads()

@state.field("threads")
async def resolve_state_threads(obj, *_):
    nextline = get_nextline()
    if nextline.state is None:
        return []
    state = nextline.state.data
    from pprint import pprint
    # pprint(state)
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
    # pprint([
    #     (thid, thda)
    #     for thid, thda in state.items()
    #     if any([not tada['finished'] for tada in thda.values()])
    # ])
    return ret

@subscription.source("state")
async def state_generator(obj, info):
    while True:
        await event.wait()
        yield {}
        event.clear()

@subscription.field("state")
async def state_resolver(state, info):
    return state

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

class Event_ts(asyncio.Event):
    '''A thread-safe asyncio event

    Code copied from
    https://stackoverflow.com/a/33006667/7309855

    '''
    def set(self):
        self._loop.call_soon_threadsafe(super().set)
    def clear(self):
        self._loop.call_soon_threadsafe(super().clear)

nextline_holder = []
event = Event_ts()

def get_nextline():
    if not nextline_holder:
        nextline_holder.append(Nextline(statement, breaks, event=event))
    return nextline_holder[0]

async def poll(nextline):
    while True:
        event.set()
        await asyncio.sleep(2)

async def intract(nextline):
    print(nextline.status)
    await asyncio.sleep(0.1)
    print(nextline.nthreads())
    while nextline.status == "running":
        if nextline.state.prompting:
            thread_asynctask_id = nextline.state.prompting[0]
            pdb_ci = nextline.pdb_ci_registry.get_ci(thread_asynctask_id)
            commands = deque(['w', 'list', 'll', 'next'])
            nprompts = pdb_ci.nprompts - 1
            while not pdb_ci.ended:
                if nprompts < pdb_ci.nprompts:
                    print(pdb_ci.stdout, end='')
                    command = commands.popleft()
                    print(command)
                    pdb_ci.send_pdb_command(command)
                nprompts = pdb_ci.nprompts
                await asyncio.sleep(1)
        await asyncio.sleep(1)
    print(nextline.nthreads())

    await nextline.wait()

async def run_nextline():
    nextline = get_nextline()
    print(nextline.status)
    if nextline.status == 'initialized':
        # asyncio.create_task(poll(nextline))
        nextline.run()
        # asyncio.create_task(intract(nextline))
    return

def reset_nextline():
    nextline_holder[:] = []
    get_nextline()
    event.set()

@mutation.field("exec")
async def resolve_exec(_, info):
    print(_)
    print(info)
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
