from datetime import datetime
from typing import List, Type, Union

from sqlalchemy import ForeignKey, MetaData, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# https://docs.sqlalchemy.org/en/14/core/constraints.html#configuring-a-naming-convention-for-a-metadata-collection
# https://github.com/simonsobs/acondbs/blob/7b4e5ab967ce/acondbs/db/sa.py
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    metadata = metadata


class Hello(Base):
    __tablename__ = "hello"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message: Mapped[Union[str, None]]


class Run(Base):
    __tablename__ = "run"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int] = mapped_column(unique=True)
    state: Mapped[Union[str, None]]
    started_at: Mapped[Union[datetime, None]]
    ended_at: Mapped[Union[datetime, None]]
    script: Mapped[Union[str, None]]
    exception: Mapped[Union[str, None]]

    traces: Mapped[List["Trace"]] = relationship(back_populates="run")
    prompts: Mapped[List["Prompt"]] = relationship(back_populates="run")
    stdouts: Mapped[List["Stdout"]] = relationship(back_populates="run")

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.run_no!r}>"


class Trace(Base):
    __tablename__ = "trace"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int]
    trace_no: Mapped[int]
    state: Mapped[str]
    thread_no: Mapped[int]
    task_no: Mapped[Union[int, None]]
    started_at: Mapped[datetime]
    ended_at: Mapped[Union[datetime, None]]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped[Run] = relationship(back_populates='traces')

    prompts: Mapped[List["Prompt"]] = relationship(back_populates="trace")
    stdouts: Mapped[List["Stdout"]] = relationship(back_populates="trace")

    __table_args__ = (UniqueConstraint("run_no", "trace_no"),)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.trace_no!r}>"


class Prompt(Base):
    __tablename__ = "prompt"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int]
    trace_no: Mapped[int]
    prompt_no: Mapped[int]
    open: Mapped[bool]
    event: Mapped[str]
    started_at: Mapped[datetime]
    file_name: Mapped[Union[str, None]]
    line_no: Mapped[Union[int, None]]
    stdout: Mapped[Union[str, None]]
    command: Mapped[Union[str, None]]
    ended_at: Mapped[Union[datetime, None]]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped[Run] = relationship(back_populates='prompts')

    trace_id: Mapped[int] = mapped_column(ForeignKey('trace.id'))
    trace: Mapped[Trace] = relationship(back_populates='prompts')

    __table_args__ = (UniqueConstraint("run_no", "prompt_no"),)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id!r}>"


class Stdout(Base):
    __tablename__ = "stdout"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_no: Mapped[int]
    trace_no: Mapped[int]
    text: Mapped[Union[str, None]]
    written_at: Mapped[Union[datetime, None]]

    run_id: Mapped[int] = mapped_column(ForeignKey('run.id'))
    run: Mapped[Run] = relationship(back_populates='stdouts')

    trace_id: Mapped[int] = mapped_column(ForeignKey('trace.id'))
    trace: Mapped[Trace] = relationship(back_populates='stdouts')

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.text!r}>"


ModelType = Union[Type[Run], Type[Trace], Type[Prompt], Type[Stdout]]
# https://python-forum.io/thread-27697.html
