'''
uvicorn nextlinegraphql:app
'''

from pathlib import Path

import asyncio
from ariadne import (
    gql,
    QueryType,
    SubscriptionType,
    load_schema_from_path,
    make_executable_schema
    )
from ariadne.asgi import GraphQL

##__________________________________________________________________||
_THISDIR = Path(__file__).resolve().parent
_SCHEMADIR = _THISDIR / 'schema/'
type_defs = load_schema_from_path(_SCHEMADIR)

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
schema = make_executable_schema(type_defs, [query, subscription])
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
