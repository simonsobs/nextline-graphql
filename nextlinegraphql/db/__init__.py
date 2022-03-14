from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .write import write_db

__all__ = ["init_db", "write_db"]


def init_db(url: str):
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False},
    )
    models.Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
