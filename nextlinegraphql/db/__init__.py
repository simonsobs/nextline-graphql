from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config
from alembic import command

from . import models
from .write import write_db

__all__ = ["init_db", "write_db"]


def init_db(url: str):
    run_alembic_upgrade()
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
    )
    models.Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def run_alembic_upgrade():
    here = Path(__file__).resolve().parent
    config_path = here.joinpath("alembic.ini")
    config = Config(str(config_path))
    command.upgrade(config, "head")
