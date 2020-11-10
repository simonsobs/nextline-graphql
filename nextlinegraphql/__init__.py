'''
uvicorn nextlinegraphql:app
uvicorn --reload --reload-dir nextline-graphql nextlinegraphql:app
'''

from ariadne.asgi import GraphQL
from starlette.middleware.cors import CORSMiddleware

from .schema import schema

##__________________________________________________________________||
app = CORSMiddleware(GraphQL(schema, debug=True), allow_origins=['*'], allow_methods=("GET", "POST", "OPTIONS"))

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
