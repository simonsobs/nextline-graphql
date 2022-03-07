from __future__ import annotations

import dataclasses

import strawberry
from strawberry.types import Info

from typing import TYPE_CHECKING, AsyncGenerator, List, Optional

if TYPE_CHECKING:
    from nextline import Nextline

AGen = AsyncGenerator


def resolve_source(info: Info, file_name: Optional[str] = None) -> List[str]:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source(file_name)


@strawberry.type
class Query:
    source: List[str] = strawberry.field(resolver=resolve_source)


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


schema = strawberry.Schema(query=Query, subscription=Subscription)
