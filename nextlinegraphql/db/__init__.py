import contextlib
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path
from typing import Iterator, Optional

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from . import models
from .write import write_db

__all__ = ['DB', 'write_db']


def create_tables(engine: Engine):
    '''Define tables in the database based on the ORM models .

    https://docs.sqlalchemy.org/en/20/orm/quickstart.html#emit-create-table-ddl
    '''
    models.Base.metadata.create_all(bind=engine)


@dataclass
class DB:
    '''The interface to the SQLAlchemy database.'''

    url: str = 'sqlite://'
    create_engine_kwargs: dict = field(default_factory=dict)
    _engine: Optional[Engine] = field(init=False, repr=False, default=None)

    @property
    def engine(self) -> Engine:
        '''The engine with the latest alembic migration version of the table definitions.

        https://docs.sqlalchemy.org/en/20/orm/quickstart.html#create-an-engine
        '''
        if self._engine is None:
            logger = getLogger(__name__)
            logger.info(f"SQLAlchemy DB URL: {self.url}")
            self._engine = create_engine(self.url, **self.create_engine_kwargs)
            migrate_to_head(self._engine)
            create_tables(self._engine)  # NOTE: unnecessary as alembic is used
            with self._engine.connect() as connection:
                context = MigrationContext.configure(connection)
                rev = context.get_current_revision()
            logger.info(f"Alembic migration version: {rev!s}")
        return self._engine

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        '''A database session with session event hooks.

        The session is yielded within the outer context. The inner context, which exits
        with commit or rollback, can be used as follows:

            with db.session() as session:
                with session.begin():
                    ...

        https://docs.sqlalchemy.org/en/20/orm/session_basics.html
        '''
        with Session(self.engine) as session:
            yield session


ALEMBIC_INI = str(Path(__file__).resolve().parent / 'alembic.ini')


def migrate_to_head(engine):
    '''Run alembic to upgrade the database to the latest version.'''
    config = Config(ALEMBIC_INI)

    # TODO: Arrange config so that logging doesn't need to be conditionally
    # configured in alembic/env.py

    # from alembic import command
    # command.upgrade(config, "head")

    # NOTE: The commented out lines of command.upgrade() above would work fine
    # for a persistent DB. Here, the following code is instead used so that the
    # migration actually takes place for an in-memory DB as well for testing.

    script = ScriptDirectory.from_config(config)

    def upgrade(rev: str, context):
        del context
        return script._upgrade_revs('head', rev)

    context = EnvironmentContext(config, script, fn=upgrade)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=models.Base.metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
