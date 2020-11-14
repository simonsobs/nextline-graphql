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
async def resolve_state_nthread(obj, *_):
    nextline = get_nextline()
    if nextline.state is None:
        return []
    return [
        { "threadId": str(thid) } for thid, thda in nextline.state.data.items()
        if any([not tada['finished'] for tada in thda.values()])
    ]

@subscription.source("state")
async def state_generator(obj, info):
    while True:
        yield {}
        await event.wait()
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
import script
script.run()
""".lstrip()

breaks = {
    # '__main__': ['<module>'],
    'script': ['run', 'task', 'task_imp', 'atask']
}

nextline_holder = []
event = asyncio.Event()

def get_nextline():
    if not nextline_holder:
        nextline_holder.append(Nextline(statement, breaks))
    return nextline_holder[0]

async def poll(nextline):
    while True:
        event.set()
        print(nextline)
        await asyncio.sleep(2.0)

async def intract(nextline):
    print(nextline.status)
    await asyncio.sleep(0.1)
    print(nextline.nthreads())
    while nextline.status == "running":
        if nextline.pdb_cis:
            pdb_ci = nextline.pdb_cis[0]
            commands = deque(['w', 'list', 'll', 'next'])
            nprompts = pdb_ci.nprompts - 1
            while not pdb_ci.ended:
                if nprompts < pdb_ci.nprompts:
                    print(pdb_ci.stdout, end='')
                    command = commands.popleft()
                    print(command)
                    pdb_ci.send_pdb_command(command)
                nprompts = pdb_ci.nprompts
                await asyncio.sleep(0.5)
        await asyncio.sleep(0.5)
    print(nextline.nthreads())

    await nextline.wait()

async def run_nextline():
    nextline = get_nextline()
    print(nextline.status)
    if nextline.status == 'initialized':
        asyncio.create_task(poll(nextline))
        nextline.run()
        asyncio.create_task(intract(nextline))
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

##__________________________________________________________________||
bindables = [query, mutation, subscription, state]

##__________________________________________________________________||
