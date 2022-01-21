"""
uvicorn --factory --reload --reload-dir nextline-graphql --reload-dir nextline nextlinegraphql:create_app
"""

__all__ = ["create_app"]

from ariadne.asgi import GraphQL

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .schema import schema


##__________________________________________________________________||
class WGraphQL(GraphQL):
    """Wrap GraphQL for introspection"""

    async def __call__(self, scope, receive, send):
        # print(scope)
        # print(receive)
        # print(send)
        await super().__call__(scope, receive, send)

    async def handle_websocket_message(
        self, message, websocket, subscriptions
    ):
        # print(message)
        # print(websocket)
        # print(subscriptions)
        await super().handle_websocket_message(
            message, websocket, subscriptions
        )


def create_app():

    # app_ = GraphQL(schema, debug=True)
    app_ = WGraphQL(schema, debug=True)

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    app = Starlette(debug=True, middleware=middleware)
    app.mount("/", app_)

    return app


##__________________________________________________________________||
# remove args so that they won't be processed in the executing script
# TODO This should be properly handled and tested
import sys  # noqa: E402

sys.argv[1:] = []

##__________________________________________________________________||
from ._version import get_versions  # noqa: E402

__version__ = get_versions()["version"]
"""str: version

The version string, e.g., "0.1.2", "0.1.2+83.ga093a20.dirty".
generated from git tags by versioneer.

Versioneer: https://github.com/warner/python-versioneer

"""

del get_versions

##__________________________________________________________________||
