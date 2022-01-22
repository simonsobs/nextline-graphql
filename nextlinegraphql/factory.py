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


from . import db


def get_context_value(request):
    # https://stackoverflow.com/a/60899736/7309855
    return {"request": request, "dbsession": db.Session}


def create_app():

    app_ = WGraphQL(schema, context_value=get_context_value, debug=True)

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
