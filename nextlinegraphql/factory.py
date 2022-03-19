import asyncio
import contextlib
from dynaconf import Dynaconf

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy.future import select
from sqlalchemy import func

from typing import Optional, Any

from nextline import Nextline

from .strawberry_fix import GraphQL
from .schema import schema
from .db import init_db, write_db, models as db_models
from .example_script import statement
from .logging import configure_logging


def create_app(config: Optional[Dynaconf] = None):

    if config is None:
        from .config import settings

        config = settings

    configure_logging(config.logging)

    db = None
    nextline: Nextline

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
        nonlocal db, nextline
        db = init_db(config.db.url)
        run_no_start_from = 1
        with db() as session:
            stmt = select(db_models.Run, func.max(db_models.Run.run_no))
            model = session.execute(stmt).scalar_one_or_none()
            if model:
                run_no_start_from = model.run_no + 1
        nextline = Nextline(statement, run_no_start_from)
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
