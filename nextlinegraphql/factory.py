import asyncio
import contextlib
from dynaconf import Dynaconf

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from typing import Optional, Any

from nextline import Nextline

from .strawberry_fix import GraphQL
from .schema import schema
from .db import init_db, write_db
from .example_script import statement


def create_app(config: Optional[Dynaconf] = None):

    if config is None:
        from .config import settings

        config = settings

    db = init_db(config.db.url)
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
