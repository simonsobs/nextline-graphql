__all__ = ['DB', 'write_db']

import contextlib
from logging import getLogger
from typing import Mapping

from dynaconf import Dynaconf
from nextline import Nextline
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.applications import Starlette

from nextlinegraphql import spec
from nextlinegraphql.decorator import asynccontextmanager

from . import models
from .db import DB
from .write import write_db


class Plugin:
    def __init__(self, config: Dynaconf):
        self._db = DB(config.db['url'])

    @spec.hookimpl
    def initial_run_no(self):
        if self._db is None:
            return None
        with self._db.session() as session:
            last_run = self._last_run(session)
            if last_run is None:
                return None
            else:
                return last_run.run_no + 1

    @spec.hookimpl
    def initial_script(self):
        if self._db is None:
            return None
        with self._db.session() as session:
            last_run = self._last_run(session)
            if last_run is None:
                return None
            else:
                return last_run.script

    def _last_run(self, session: Session):
        stmt = select(models.Run, func.max(models.Run.run_no))
        if model := session.execute(stmt).scalar_one_or_none():
            return model
        else:
            logger = getLogger(__name__)
            msg = "No previous runs were found in the DB"
            logger.info(msg)
            return None

    @spec.hookimpl
    @asynccontextmanager
    async def lifespan(self, app: Starlette, nextline: Nextline):
        async with contextlib.AsyncExitStack() as stack:
            if self._db:
                await stack.enter_async_context(write_db(nextline, self._db))
            yield

    @spec.hookimpl
    async def get_context(self, context: Mapping):
        return {'db': self._db}
