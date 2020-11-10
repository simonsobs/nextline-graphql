'''
uvicorn nextlinegraphql:app
uvicorn --reload --reload-dir nextline-graphql nextlinegraphql:app
'''

from ariadne import make_executable_schema
from ariadne.asgi import GraphQL

from .schema import type_defs
from .bindables import query, mutation, subscription

##__________________________________________________________________||
schema = make_executable_schema(type_defs, [query, mutation, subscription])
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
