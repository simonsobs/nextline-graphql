import asyncio
import contextlib
import datetime
import traceback
from strawberry.asgi import GraphQL as GraphQL_
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from typing import Optional, Any

from nextline import Nextline

from .schema import schema
from .db import Db
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


async def write_db(nextline: Nextline, db) -> None:
    async for state_name in nextline.subscribe_state():
        run_no = nextline.run_no
        now = datetime.datetime.now()
        with db.Session.begin() as session:
            state_change = db.models.StateChange(
                name=state_name, datetime=now, run_no=run_no
            )
            run = (
                session.query(db.models.Run)
                .filter_by(run_no=run_no)
                .one_or_none()
            )
            if run is None:
                run = db.models.Run(run_no=run, script=nextline.statement)
                session.add(run)
            run.state = state_name
            if state_name == "running":
                run.started_at = now
            if state_name == "exited":
                run.ended_at = now
            if state_name == "finished":
                exc = nextline.exception()
                if exc:
                    run.exception = "".join(
                        traceback.format_exception(
                            type(exc), exc, exc.__traceback__
                        )
                    )
            session.add(state_change)
            session.commit()


def create_app():

    db = Db()
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
        yield
        await nextline.close()
        await task

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
