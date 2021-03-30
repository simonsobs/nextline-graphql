'''
uvicorn nextlinegraphql:app
uvicorn --reload --reload-dir nextline-graphql nextlinegraphql:app
'''

from ariadne.asgi import GraphQL

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .schema import schema

##__________________________________________________________________||
middleware = [
    Middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
]

app = Starlette(debug=True, middleware=middleware)
app.mount("/", GraphQL(schema, debug=True))

##__________________________________________________________________||
# remove args so that they won't be processed in the executing script
# TODO This should be properly handled and tested
import sys
sys.argv[1:] = []

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
