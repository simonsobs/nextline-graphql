from __future__ import annotations

import dataclasses
import traceback

import strawberry
from strawberry.types import Info

from typing import TYPE_CHECKING, AsyncGenerator, List, Optional

if TYPE_CHECKING:
    from nextline import Nextline

from ..nl import run_nextline, reset_nextline

AGen = AsyncGenerator


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
class Query:
    global_state: str = strawberry.field(resolver=query_global_state)
    run_no: int = strawberry.field(resolver=query_run_no)
    source: List[str] = strawberry.field(resolver=query_source)
    source_line: str = strawberry.field(resolver=query_source_line)
    exception: Optional[str] = strawberry.field(resolver=query_exception)


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
    from ..schema.bindables import subscribe_stdout as s

    async for y in s():
        if nextline.state == "running":
            yield y


@strawberry.type
class Subscription:
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
