import asyncio
import contextlib
from dynaconf import Dynaconf
from logging import getLogger

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

        logger = getLogger(__name__)

        run_no_start_from = 1

        try:
            db, _ = init_db(config.db)
        except BaseException:
            logger.exception("failed to initialize DB ")
            db = None

        if db:
            try:
                with db() as session:
                    stmt = select(
                        db_models.Run,
                        func.max(db_models.Run.run_no),
                    )
                    if model := session.execute(stmt).scalar_one_or_none():
                        run_no_start_from = model.run_no + 1
                    else:
                        msg = "No previous runs were found in the DB"
                        logger.info(msg)
            except BaseException:
                msg = "failed to obtain the last run number in the DB"
                logger.exception(msg)
                db = None

        nextline = Nextline(statement, run_no_start_from)
        if db:
            task = asyncio.create_task(write_db(nextline, db))
        else:
            logger.error("Starting without DB")
            task = None

        try:
            yield
        finally:
            await asyncio.wait_for(nextline.close(), timeout=3)
            if task:
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
