'''
uvicorn nextlinegraphql:app
'''

import asyncio
from ariadne import (
    gql,
    QueryType,
    SubscriptionType,
    make_executable_schema
    )
from ariadne.asgi import GraphQL

##__________________________________________________________________||
type_def = gql("""
    type Query {
        hello: String!
    }

    type Subscription {
        counter: Int!
    }
""")

##__________________________________________________________________||
query = QueryType()
subscription = SubscriptionType()

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
schema = make_executable_schema(type_def, [query, subscription])
app = GraphQL(schema, debug=True)

##__________________________________________________________________||

##__________________________________________________________________||
from ._version import get_versions
__version__ = get_versions()['version']
"""str: version

The version string, e.g., "0.1.2", "0.1.2+83.ga093a20.dirty".
generated from git tags by versioneer.

Versioneer: https://github.com/warner/python-versioneer

"""

del get_versions

##__________________________________________________________________||
