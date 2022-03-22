from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from alembic.runtime.environment import EnvironmentContext
from logging import getLogger

from typing import Dict

from . import models
from .write import write_db

__all__ = ["init_db", "write_db"]


def init_db(config: Dict):

    url = config["url"]

    logger = getLogger(__name__)
    logger.info(f"SQLAlchemy DB URL: {url}")

    engine = create_engine(url)

    run_alembic_upgrade(engine)

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        rev = context.get_current_revision()
    logger.info(f"Alembic migration version: {rev!s}")

    models.Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_alembic_upgrade(engine):
    here = Path(__file__).resolve().parent
    config_path = here.joinpath("alembic.ini")
    config = Config(str(config_path))

    # TODO: Arrange config so that logging doesn't need to be conditionally
    # configured in alembic/env.py

    # from alembic import command
    # command.upgrade(config, "head")

    # NOTE: The commented out lines of command.upgrade() above would work fine
    # for a persistent DB. Here, the following code is instead used so that the
    # migration actually takes place for an in-memory DB as well for testing.

    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):
        del context
        return script._upgrade_revs("head", rev)

    context = EnvironmentContext(config, script, fn=upgrade)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=models.Base.metadata,
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()
