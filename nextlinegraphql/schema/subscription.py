from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncGenerator, List

import strawberry
from strawberry.types import Info

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


async def subscribe_prompting(info: Info, trace_id: int) -> AGen[PromptingData, None]:
    nextline: Nextline = info.context["nextline"]
    async for y in nextline.subscribe_prompt_info_for(trace_id):
        if not y.file_name:
            # the initial yield at the beginning of a thread or task
            continue
        y = PromptingData(
            prompting=y.prompt_no if y.open else 0,
            file_name=y.file_name,
            line_no=y.line_no,
            trace_event=y.event,
        )
        yield y


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
