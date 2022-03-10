import datetime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey


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
    run_no = Column(Integer, ForeignKey("run.run_no"))


class Run(Base):
    __tablename__ = "run"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, index=True)
    state = Column(String)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    script = Column(Text)
    exception = Column(Text)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.run_no!r}>"


class Trace(Base):
    __tablename__ = "trace"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, ForeignKey("run.run_no"))
    trace_id = Column(Integer, index=True)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.trace_id!r}>"


class Prompt(Base):
    __tablename__ = "prompt"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, ForeignKey("run.run_no"))
    trace_id = Column(Integer, ForeignKey("trace.trace_id"))
    started_at = Column(DateTime)
    file_name = Column(String)
    line_no = Column(Integer)
    event = Column(String)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id!r}>"
