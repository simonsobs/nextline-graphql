from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, AsyncIterator, List, Tuple

import strawberry
from strawberry.types import Info

if TYPE_CHECKING:
    from nextline import Nextline


@strawberry.type
class PromptingData:
    prompting: int
    file_name: str
    line_no: int
    trace_event: str


async def subscribe_counter() -> AsyncIterator[int]:
    for i in range(5):
        await asyncio.sleep(0)
        yield i + 1


def subscribe_state(info: Info) -> AsyncIterator[str]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_state()


def subscribe_run_no(info: Info) -> AsyncIterator[int]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_run_no()


def subscribe_trace_ids(info: Info) -> AsyncIterator[Tuple[int, ...]]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_trace_ids()


async def subscribe_prompting(
    info: Info, trace_id: int
) -> AsyncIterator[PromptingData]:
    nextline: Nextline = info.context["nextline"]
    async for i in nextline.subscribe_prompt_info_for(trace_id):
        if not i.file_name:
            # the initial yield at the beginning of a thread or task
            continue
        assert i.line_no is not None
        assert i.event is not None
        y = PromptingData(
            prompting=i.prompt_no if i.open else 0,
            file_name=i.file_name,
            line_no=i.line_no,
            trace_event=i.event,
        )
        yield y


async def subscribe_stdout(info: Info) -> AsyncIterator[str]:
    nextline: Nextline = info.context["nextline"]
    async for i in nextline.subscribe_stdout():
        assert i.text is not None
        yield i.text


def subscribe_continuous_enabled(info: Info) -> AsyncIterator[bool]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_continuous_enabled()


@strawberry.type
class Subscription:
    counter: AsyncIterator[int] = strawberry.field(
        is_subscription=True, resolver=subscribe_counter
    )
    state: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_state
    )
    run_no: AsyncIterator[int] = strawberry.field(
        is_subscription=True, resolver=subscribe_run_no
    )
    trace_ids: AsyncIterator[List[int]] = strawberry.field(
        is_subscription=True, resolver=subscribe_trace_ids
    )
    prompting: AsyncIterator[PromptingData] = strawberry.field(
        is_subscription=True, resolver=subscribe_prompting
    )
    stdout: AsyncIterator[str] = strawberry.field(
        is_subscription=True, resolver=subscribe_stdout
    )
    continuous_enabled: AsyncIterator[bool] = strawberry.field(
        is_subscription=True, resolver=subscribe_continuous_enabled
    )
