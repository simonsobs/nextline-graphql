import datetime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship


Base = declarative_base()


class Hello(Base):
    __tablename__ = "hello"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)


class StateChange(Base):
    __tablename__ = "state_change_log"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    datetime = Column(DateTime(), default=lambda: datetime.datetime.now())
    run_no = Column(ForeignKey("run.run_no"))


class Run(Base):
    __tablename__ = "run"
    run_no = Column(Integer, primary_key=True, index=True)
    state_changes = relationship("StateChange", backref="run")
