from __future__ import annotations
import asyncio
import strawberry
from strawberry.types import Info
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from nextline import Nextline


async def mutate_exec(info: Info) -> bool:

    nextline: Nextline = info.context["nextline"]

    async def wait():
        await nextline.run()

    asyncio.create_task(wait())
    return True


def mutate_reset(info: Info, statement: Optional[str] = None):
    nextline: Nextline = info.context["nextline"]
    nextline.reset(statement=statement)
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
