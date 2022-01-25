import asyncio
from ariadne.asgi import GraphQL

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .schema import schema
from .db import Db
from .nl import get_nextline


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


async def monitor_state(db):
    nextline = get_nextline()
    async for s in nextline.subscribe_global_state():
        with db.Session.begin() as session:
            model = db.models.StateChange(name=s)
            session.add(model)
            session.commit()


def create_app():

    db = Db()

    asyncio.create_task(monitor_state(db))

    app_ = WGraphQL(
        schema,
        context_value=lambda request: {
            "request": request,
            "db": db,
            "nextline": get_nextline(),
        },
        debug=True,
    )

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
