from __future__ import annotations
import traceback
import strawberry
from strawberry.types import Info
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from typing import TYPE_CHECKING, List, Optional, cast

from . import types
from ..db import models as db_models

if TYPE_CHECKING:
    from nextline import Nextline


def query_hello(info: Info) -> str:
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent


def query_state(info: Info) -> str:
    nextline: Nextline = info.context["nextline"]
    return nextline.state


def query_run_no(info: Info) -> int:
    nextline: Nextline = info.context["nextline"]
    return nextline.run_no


def query_source(info: Info, file_name: Optional[str] = None) -> List[str]:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source(file_name)


def query_source_line(
    info: Info, line_no: int, file_name: Optional[str]
) -> str:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source_line(line_no, file_name)


def query_exception(info: Info) -> Optional[str]:
    nextline: Nextline = info.context["nextline"]
    if exc := nextline.exception():
        return "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
    return None


def query_runs(info: Info) -> List[types.RunHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Run))
    return [types.RunHistory.from_model(m) for m in models]


def query_traces(info: Info) -> List[types.TraceHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Trace))
    return [types.TraceHistory.from_model(m) for m in models]


def query_prompt(info: Info) -> List[types.PromptHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Prompt))
    return [types.PromptHistory.from_model(m) for m in models]


def query_stdouts(info: Info) -> List[types.StdoutHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Stdout))
    return [types.StdoutHistory.from_model(m) for m in models]


@strawberry.type
class History:
    runs: List[types.RunHistory] = strawberry.field(resolver=query_runs)
    traces: List[types.TraceHistory] = strawberry.field(resolver=query_traces)
    prompts: List[types.PromptHistory] = strawberry.field(
        resolver=query_prompt
    )
    stdouts: List[types.StdoutHistory] = strawberry.field(
        resolver=query_stdouts
    )


@strawberry.type
class Query:
    hello: str = strawberry.field(resolver=query_hello)
    state: str = strawberry.field(resolver=query_state)
    run_no: int = strawberry.field(resolver=query_run_no)
    source: List[str] = strawberry.field(resolver=query_source)
    source_line: str = strawberry.field(resolver=query_source_line)
    exception: Optional[str] = strawberry.field(resolver=query_exception)

    @strawberry.field
    def history(self, info: Info) -> History:
        db = info.context["db"]
        with db() as session:
            info.context["session"] = session
            return History()
