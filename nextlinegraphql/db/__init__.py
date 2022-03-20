from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic import command
from logging import getLogger

from . import models
from .write import write_db

__all__ = ["init_db", "write_db"]


def init_db(url: str):

    logger = getLogger(__name__)
    logger.info(f"SQLAlchemy DB URL: {url}")

    run_alembic_upgrade()

    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
    )

    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        rev = context.get_current_revision()
    logger.info(f"Alembic migration version: {rev!s}")

    models.Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_alembic_upgrade():
    here = Path(__file__).resolve().parent
    config_path = here.joinpath("alembic.ini")
    config = Config(str(config_path))
    # TODO: Arrange config so that logging doesn't need to be conditionally
    # configured in alembic/env.py
    command.upgrade(config, "head")
