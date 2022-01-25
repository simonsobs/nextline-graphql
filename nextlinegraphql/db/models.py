import datetime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, DateTime


Base = declarative_base()


class Hello(Base):
    __tablename__ = "hello"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)


class StateChange(Base):
    __tablename__ = "state_change_log"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    time = Column(DateTime(), default=lambda: datetime.datetime.now())
