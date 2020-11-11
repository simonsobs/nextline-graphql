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
async def resolve_state_(obj, *_):
    nextline = get_nextline()
    return nextline.status

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

@subscription.source("status")
async def status_generator(obj, info):
    previous = None
    while True:
        nextline = get_nextline()
        if previous == nextline.status:
            await asyncio.sleep(0.1)
            continue
        previous = nextline.status
        yield nextline.status
        if nextline.status == 'finished':
            break

@subscription.field("status")
async def status_resolver(status, info):
    return status

##__________________________________________________________________||
_THIS_DIR = Path(__file__).resolve().parent
statement = """
import sys
sys.path.insert(0, "{}")
import script
script.run()
""".lstrip().format(_THIS_DIR)

del _THIS_DIR

breaks = {
    # '__main__': ['<module>'],
    # 'script': ['run', 'task', 'task_imp', 'atask']
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
        await asyncio.sleep(1.0)

async def run_nextline():
    nextline = get_nextline()
    print(nextline.status)
    if nextline.status == 'initialized':
        asyncio.create_task(poll(nextline))
        nextline.run()
    return

@mutation.field("exec")
async def resolve_exec(_, info):
    print(_)
    print(info)
    await run_nextline()
    return True

##__________________________________________________________________||
bindables = [query, mutation, subscription, state]

##__________________________________________________________________||
