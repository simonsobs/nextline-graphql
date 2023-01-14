from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

import strawberry
from strawberry.types import Info

if TYPE_CHECKING:
    from nextline import Nextline


async def mutate_exec(info: Info) -> bool:

    nextline: Nextline = info.context["nextline"]

    async def wait():
        await nextline.run()

    asyncio.create_task(wait())
    return True


async def mutate_reset(info: Info, statement: Optional[str] = None):
    nextline: Nextline = info.context["nextline"]
    await nextline.reset(statement=statement)
    return True


def mutate_send_pdb_command(
    info: Info, command: str, prompt_no: int, trace_no: int
) -> bool:
    nextline: Nextline = info.context["nextline"]
    nextline.send_pdb_command(command, prompt_no, trace_no)
    return True


def mutate_interrupt(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    nextline.interrupt()
    return True


def mutate_terminate(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    nextline.terminate()
    return True


def mutate_kill(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    nextline.kill()
    return True


@strawberry.type
class Mutation:
    exec: bool = strawberry.field(resolver=mutate_exec)
    reset: bool = strawberry.field(resolver=mutate_reset)
    send_pdb_command: bool = strawberry.field(resolver=mutate_send_pdb_command)
    interrupt: bool = strawberry.field(resolver=mutate_interrupt)
    terminate: bool = strawberry.field(resolver=mutate_terminate)
    kill: bool = strawberry.field(resolver=mutate_kill)
