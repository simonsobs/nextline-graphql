from __future__ import annotations
import traceback
import strawberry
from strawberry.types import Info
from typing import TYPE_CHECKING, List, Optional, Iterable

from . import types

if TYPE_CHECKING:
    from nextline import Nextline
    from ..db import Db


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


def query_state_changes(info: Info) -> List[types.StateChange]:
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        models = session.query(db.models.StateChange).all()  # type: ignore
        return [
            types.StateChange(
                name=m.name, datetime=m.datetime, run_no=m.run_no
            )
            for m in models
        ]


def query_runs(info: Info) -> List[types.RunHistory]:
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        models: Iterable[db.models.Run] = session.query(db.models.Run)  # type: ignore
        return [
            types.RunHistory(
                run_no=m.run_no,
                state=m.state,
                started_at=m.started_at,
                ended_at=m.ended_at,
                script=m.script,
                exception=m.exception,
            )
            for m in models
        ]


def query_traces(info: Info) -> List[types.TraceHistory]:
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        models: Iterable[db.models.Trace] = session.query(db.models.Trace)  # type: ignore
        return [
            types.TraceHistory(
                trace_id=m.trace_id,
                run_no=m.run_no,
                started_at=m.started_at,
                ended_at=m.ended_at,
            )
            for m in models
        ]


def query_prompt(info: Info) -> List[types.PromptHistory]:
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        models: Iterable[db.models.Prompt] = session.query(db.models.Prompt)  # type: ignore
        return [
            types.PromptHistory(
                run_no=m.run_no,
                trace_id=m.trace_id,
                prompt_no=m.prompt_no,
                event=m.event,
                started_at=m.started_at,
                file_name=m.file_name,
                line_no=m.line_no,
            )
            for m in models
        ]


@strawberry.type
class History:
    runs: List[types.RunHistory] = strawberry.field(resolver=query_runs)
    traces: List[types.TraceHistory] = strawberry.field(resolver=query_traces)
    prompts: List[types.PromptHistory] = strawberry.field(
        resolver=query_prompt
    )


async def query_history(info: Info) -> History:
    return History()


@strawberry.type
class Query:
    hello: str = strawberry.field(resolver=query_hello)
    state: str = strawberry.field(resolver=query_state)
    run_no: int = strawberry.field(resolver=query_run_no)
    source: List[str] = strawberry.field(resolver=query_source)
    source_line: str = strawberry.field(resolver=query_source_line)
    exception: Optional[str] = strawberry.field(resolver=query_exception)
    state_changes: types.StateChange = strawberry.field(
        resolver=query_state_changes
    )
    runs: List[types.RunHistory] = strawberry.field(resolver=query_runs)
    history: History = strawberry.field(resolver=query_history)
