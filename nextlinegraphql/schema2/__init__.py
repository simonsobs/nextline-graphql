from __future__ import annotations

import asyncio
import dataclasses
import datetime
import traceback

import strawberry
from strawberry.types import Info

from typing import TYPE_CHECKING, AsyncGenerator, List, Optional, Iterable

from ..nl import run_nextline, reset_nextline

if TYPE_CHECKING:
    from nextline import Nextline
    from ..db import Db

AGen = AsyncGenerator


def query_hello(info: Info) -> str:
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent


def query_global_state(info: Info) -> str:
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


@strawberry.type
class StateChange:
    name: str
    datetime: datetime.datetime
    run_no: int


@strawberry.type
class Run:
    run_no: int
    state: Optional[str] = None
    started_at: Optional[datetime.date] = None
    ended_at: Optional[datetime.date] = None
    script: Optional[str] = None
    exception: Optional[str] = None


def query_state_changes(info: Info) -> List[StateChange]:
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        models = session.query(db.models.StateChange).all()  # type: ignore
        return [
            StateChange(name=m.name, datetime=m.datetime, run_no=m.run_no)
            for m in models
        ]


def query_runs(info: Info) -> List[Run]:
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        runs: Iterable[db.models.Run] = session.query(db.models.Run)  # type: ignore
        return [
            Run(
                run_no=m.run_no,
                state=m.state,
                started_at=m.started_at,
                ended_at=m.ended_at,
                script=m.script,
                exception=m.exception,
            )
            for m in runs
        ]


@strawberry.type
class Query:
    hello: str = strawberry.field(resolver=query_hello)
    global_state: str = strawberry.field(resolver=query_global_state)
    run_no: int = strawberry.field(resolver=query_run_no)
    source: List[str] = strawberry.field(resolver=query_source)
    source_line: str = strawberry.field(resolver=query_source_line)
    exception: Optional[str] = strawberry.field(resolver=query_exception)
    state_changes: StateChange = strawberry.field(resolver=query_state_changes)
    runs: List[Run] = strawberry.field(resolver=query_runs)


async def mutate_exec() -> bool:
    await run_nextline()
    return True


def mutate_reset(statement: Optional[str] = None):
    reset_nextline(statement=statement)
    return True


def mutate_send_pdb_command(info: Info, trace_id: int, command: str) -> bool:
    nextline: Nextline = info.context["nextline"]
    nextline.send_pdb_command(trace_id, command)
    return True


@strawberry.type
class Mutation:
    exec: bool = strawberry.field(resolver=mutate_exec)
    reset: bool = strawberry.field(resolver=mutate_reset)
    send_pdb_command: bool = strawberry.field(resolver=mutate_send_pdb_command)


async def subscribe_counter() -> AGen[int, None]:
    for i in range(5):
        await asyncio.sleep(0)
        yield i + 1


def subscribe_global_state(info: Info) -> AGen[str, None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_state()


def subscribe_run_no(info: Info) -> AGen[int, None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_run_no()


def subscribe_trace_ids(info: Info) -> AGen[List[int], None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_trace_ids()


@strawberry.type
class TraceState:
    prompting: int
    file_name: str
    line_no: int
    trace_event: str


async def subscribe_trace_state(
    info: Info, trace_id: int
) -> AGen[TraceState, None]:
    nextline: Nextline = info.context["nextline"]
    async for y in nextline.subscribe_prompting(trace_id):
        yield TraceState(**dataclasses.asdict(y))


async def subscribe_stdout(info: Info) -> AGen[str, None]:
    nextline: Nextline = info.context["nextline"]
    from .stream import subscribe_stdout as s

    async for y in s():
        if nextline.state == "running":
            yield y


@strawberry.type
class Subscription:
    counter: AGen[int, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_counter
    )
    global_state: AGen[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_global_state
    )
    run_no: AGen[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_run_no
    )
    trace_ids: AGen[List[int], None] = strawberry.field(
        is_subscription=True, resolver=subscribe_trace_ids
    )
    trace_state: AGen[TraceState, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_trace_state
    )
    stdout: AGen[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_stdout
    )


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
)
