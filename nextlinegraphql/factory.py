import asyncio
import datetime
import traceback
from strawberry.asgi import GraphQL as SGraphQL
from strawberry.subscriptions import GRAPHQL_WS_PROTOCOL

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from typing import Optional, Any

from .schema import schema
from .db import Db
from .nl import get_nextline


async def monitor_state(db):
    nextline = get_nextline()
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

    asyncio.create_task(monitor_state(db))

    class ESGraphQl(SGraphQL):
        async def get_context(self, request, response=None) -> Optional[Any]:
            return {
                "request": request,
                "response": response,
                "db": db,
                "nextline": get_nextline(),
            }

        def pick_preferred_protocol(self, ws):
            """Overriding for async_asgi_testclient

            Return GRAPHQL_WS_PROTOCOL if the base class returns None.
            """
            return super().pick_preferred_protocol(ws) or GRAPHQL_WS_PROTOCOL

    app_ = ESGraphQl(schema)

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
