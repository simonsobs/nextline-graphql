import asyncio
import contextlib
from strawberry.asgi import GraphQL as GraphQL_
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from typing import Optional, Any

from nextline import Nextline

from .schema import schema
from .db import init_db, write_db
from .example_script import statement


class GraphQL(GraphQL_):
    """Add a fix to the strawberry GraphQL for async_asgi_testclient"""

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            if not scope.get("subprotocols"):
                # strawberry closes the websocket connection if
                # subprotocols are empty, which is the case for
                # async_asgi_testclient.
                scope["subprotocols"] = [GRAPHQL_WS_PROTOCOL]
        await super().__call__(scope, receive, send)


def create_app():

    db = init_db()
    nextline = Nextline(statement)

    class EGraphQL(GraphQL):
        """Extend the strawberry GraphQL app

        https://strawberry.rocks/docs/integrations/asgi
        """

        async def get_context(self, request, response=None) -> Optional[Any]:
            return {
                "request": request,
                "response": response,
                "db": db,
                "nextline": nextline,
            }

    app_ = EGraphQL(schema)

    @contextlib.asynccontextmanager
    async def lifespan(app):
        del app
        task = asyncio.create_task(write_db(nextline, db))
        try:
            yield
        finally:
            await asyncio.wait_for(nextline.close(), timeout=3)
            await asyncio.wait_for(task, timeout=3)

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    app = Starlette(debug=True, lifespan=lifespan, middleware=middleware)
    app.mount("/", app_)

    return app
