from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .write import write_db

__all__ = ["Db", "write_db"]

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


class Db:
    def __init__(self):
        self.engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        self.Session = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.models = models
        self.models.Base.metadata.create_all(bind=self.engine)
