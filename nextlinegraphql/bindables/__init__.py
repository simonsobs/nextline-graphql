from pathlib import Path
import asyncio
from ariadne import QueryType, MutationType, SubscriptionType

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


@subscription.source("counter")
async def counter_generator(obj, info):
    for i in range(5):
        await asyncio.sleep(1)
        yield i


@subscription.field("counter")
def counter_resolver(count, info):
    return count + 1

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
    '__main__': ['<module>'],
    'script': ['run', 'task', 'task_imp', 'atask']
}

@mutation.field("exec")
def resolve_exec(_, info):
    print(_)
    print(info)
    nextline = Nextline(statement, breaks)
    nextline.run()
    return True

##__________________________________________________________________||
