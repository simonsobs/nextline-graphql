from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import strawberry
from strawberry.types import Info

if TYPE_CHECKING:
    from nextline import Nextline


async def mutate_exec(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    await nextline.run()
    return True


async def mutate_run_and_continue(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    await nextline.run_and_continue()
    return True


async def mutate_reset(info: Info, statement: Optional[str] = None):
    nextline: Nextline = info.context["nextline"]
    await nextline.reset(statement=statement)
    return True


async def mutate_send_pdb_command(
    info: Info, command: str, prompt_no: int, trace_no: int
) -> bool:
    nextline: Nextline = info.context["nextline"]
    await nextline.send_pdb_command(command, prompt_no, trace_no)
    return True


async def mutate_interrupt(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    await nextline.interrupt()
    return True


async def mutate_terminate(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    await nextline.terminate()
    return True


async def mutate_kill(info: Info) -> bool:
    nextline: Nextline = info.context["nextline"]
    await nextline.kill()
    return True


@strawberry.type
class Mutation:
    exec: bool = strawberry.field(resolver=mutate_exec)
    run_and_continue: bool = strawberry.field(resolver=mutate_run_and_continue)
    reset: bool = strawberry.field(resolver=mutate_reset)
    send_pdb_command: bool = strawberry.field(resolver=mutate_send_pdb_command)
    interrupt: bool = strawberry.field(resolver=mutate_interrupt)
    terminate: bool = strawberry.field(resolver=mutate_terminate)
    kill: bool = strawberry.field(resolver=mutate_kill)
