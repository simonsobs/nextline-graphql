from __future__ import annotations
import asyncio
import dataclasses
import strawberry
from strawberry.types import Info
from typing import TYPE_CHECKING, AsyncGenerator, List

if TYPE_CHECKING:
    from nextline import Nextline

from .types import PromptingData

AGen = AsyncGenerator


async def subscribe_counter() -> AGen[int, None]:
    for i in range(5):
        await asyncio.sleep(0)
        yield i + 1


def subscribe_state(info: Info) -> AGen[str, None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_state()


def subscribe_run_no(info: Info) -> AGen[int, None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_run_no()


def subscribe_trace_ids(info: Info) -> AGen[List[int], None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_trace_ids()


async def subscribe_prompting(
    info: Info, trace_id: int
) -> AGen[PromptingData, None]:
    nextline: Nextline = info.context["nextline"]
    async for y in nextline.subscribe_prompting(trace_id):
        yield PromptingData(**dataclasses.asdict(y))


async def subscribe_stdout(info: Info) -> AGen[str, None]:
    nextline: Nextline = info.context["nextline"]
    async for info in nextline.subscribe_stdout():
        yield info.text  # type: ignore


@strawberry.type
class Subscription:
    counter: AGen[int, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_counter
    )
    state: AGen[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_state
    )
    run_no: AGen[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_run_no
    )
    trace_ids: AGen[List[int], None] = strawberry.field(
        is_subscription=True, resolver=subscribe_trace_ids
    )
    prompting: AGen[PromptingData, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_prompting
    )
    stdout: AGen[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_stdout
    )
