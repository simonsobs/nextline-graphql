import asyncio
import contextlib
from dynaconf import Dynaconf
from logging import getLogger

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker

from typing import Optional, Tuple, Any

from nextline import Nextline

from .strawberry_fix import GraphQL
from .schema import schema
from .db import init_db, write_db, models as db_models
from .example_script import statement
from .logging import configure_logging


def create_app(
    config: Optional[Dynaconf] = None,
    db: Optional[sessionmaker] = None,
    engine: Optional[Engine] = None,
    nextline: Optional[Nextline] = None,
):

    if config is None:
        from .config import settings

        config = settings

    configure_logging(config.logging)

    class EGraphQL(GraphQL):
        """Extend the strawberry GraphQL app

        https://strawberry.rocks/docs/integrations/asgi
        """

        async def get_context(self, request, response=None) -> Optional[Any]:
            return {
                "request": request,
                "response": response,
                "db": db,
                "engine": engine,
                "nextline": nextline,
            }

    app_ = EGraphQL(schema)

    @contextlib.asynccontextmanager
    async def lifespan(app):
        del app
        nonlocal db, engine, nextline

        logger = getLogger(__name__)

        if not db:
            try:
                db, engine = init_db(config.db)
            except BaseException:
                logger.exception("failed to initialize DB ")
                db = None

        try:
            run_no, script = get_last_run_no_and_script(db)
        except BaseException:
            logger.exception("failed to get the last run info in the DB")
            run_no = 0
            script = statement

        run_no = run_no + 1

        if not nextline:
            nextline = Nextline(script, run_no)

        await nextline.start()

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


def get_last_run_no_and_script(db) -> Tuple[int, str]:
    """Get the last run number and the script from the DB"""

    with db() as session:
        stmt = select(db_models.Run, func.max(db_models.Run.run_no))
        if model := session.execute(stmt).scalar_one_or_none():
            return model.run_no, model.script
        else:
            logger = getLogger(__name__)
            msg = "No previous runs were found in the DB"
            logger.info(msg)
            return 0, statement
