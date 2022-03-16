from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)


Base = declarative_base()


class Hello(Base):
    __tablename__ = "hello"
    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)


class Run(Base):
    __tablename__ = "run"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, unique=True, nullable=False)
    state = Column(String)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    script = Column(Text)
    exception = Column(Text)

    traces = relationship("Trace", back_populates="run")
    prompts = relationship("Prompt", back_populates="run")
    stdouts = relationship("Stdout", back_populates="run")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.run_no!r}>"


class Trace(Base):
    __tablename__ = "trace"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, nullable=False)
    trace_no = Column(Integer, nullable=False)
    state = Column(String, nullable=False)
    thread_no = Column(Integer, nullable=False)
    task_no = Column(Integer)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime)

    run_id = Column(Integer, ForeignKey("run.id"), nullable=False)
    run = relationship("Run", back_populates="traces")

    prompts = relationship("Prompt", back_populates="trace")
    stdouts = relationship("Stdout", back_populates="trace")

    __table_args__ = (UniqueConstraint("run_no", "trace_no"),)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.trace_no!r}>"


class Prompt(Base):
    __tablename__ = "prompt"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, nullable=False)
    trace_no = Column(Integer, nullable=False)
    prompt_no = Column(Integer, nullable=False)
    open = Column(Boolean, nullable=False)
    event = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False)
    file_name = Column(String)
    line_no = Column(Integer)
    stdout = Column(String)
    command = Column(String)
    ended_at = Column(DateTime)

    run_id = Column(Integer, ForeignKey("run.id"), nullable=False)
    run = relationship("Run", back_populates="prompts")

    trace_id = Column(Integer, ForeignKey("trace.id"), nullable=False)
    trace = relationship("Trace", back_populates="prompts")

    __table_args__ = (UniqueConstraint("run_no", "prompt_no"),)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id!r}>"


class Stdout(Base):
    __tablename__ = "stdout"
    id = Column(Integer, primary_key=True, index=True)
    run_no = Column(Integer, nullable=False)
    trace_no = Column(Integer, nullable=False)
    text = Column(String)
    written_at = Column(DateTime)

    run_id = Column(Integer, ForeignKey("run.id"), nullable=False)
    run = relationship("Run", back_populates="stdouts")

    trace_id = Column(Integer, ForeignKey("trace.id"), nullable=False)
    trace = relationship("Trace", back_populates="stdouts")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.text!r}>"
