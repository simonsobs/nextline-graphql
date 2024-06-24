'''Strawberry GraphQL ASGI app with a fix for async_asgi_testclient.

Strawberry: https://strawberry.rocks
'''
from typing import TYPE_CHECKING

from strawberry.asgi import GraphQL as GraphQL_
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL

if TYPE_CHECKING:
    from strawberry.asgi import Receive, Scope, Send


class GraphQL(GraphQL_):
    """Add a fix to the strawberry GraphQL for async_asgi_testclient"""

    async def __call__(self, scope: 'Scope', receive: 'Receive', send: 'Send') -> None:
        if scope["type"] == "websocket":
            if not scope.get("subprotocols"):
                # strawberry closes the websocket connection if
                # subprotocols are empty, which is the case for
                # async_asgi_testclient.
                scope["subprotocols"] = [GRAPHQL_WS_PROTOCOL]
        return await super().__call__(scope, receive, send)
