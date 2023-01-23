from logging import getLogger
from pathlib import Path
from typing import Mapping, Optional, Tuple

from dynaconf import Dynaconf, Validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.applications import Starlette

from nextlinegraphql.custom.decorator import asynccontextmanager
from nextlinegraphql.hook import spec

from . import models
from .db import DB
from .schema import Mutation, Query, Subscription
from .write import write_db

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'
MIGRATION_CONFIG_PATH = HERE / 'migration.toml'

assert DEFAULT_CONFIG_PATH.is_file()
assert MIGRATION_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (Validator("DB.URL", must_exist=True, is_type_of=str),)

SETTINGS_FOR_MIGRATION = (str(MIGRATION_CONFIG_PATH),)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[Tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[Tuple[str, ...]]:
        if Path.cwd() == HERE:
            return SETTINGS_FOR_MIGRATION
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[Tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf):
        self._db = DB(settings.db['url'])

    @spec.hookimpl
    def initial_run_no(self):
        with self._db.session() as session:
            last_run = self._last_run(session)
            if last_run is None:
                return None
            else:
                return last_run.run_no + 1

    @spec.hookimpl
    def initial_script(self):
        with self._db.session() as session:
            last_run = self._last_run(session)
            if last_run is None:
                return None
            else:
                return last_run.script

    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)

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
    async def lifespan(self, app: Starlette, context: Mapping):
        nextline = context['nextline']
        async with write_db(nextline, self._db):
            yield

    @spec.hookimpl
    async def get_context(self, context: Mapping):
        return {'db': self._db}
