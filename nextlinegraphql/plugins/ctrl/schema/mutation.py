from pathlib import Path
from typing import Optional

import strawberry
from nextline import Nextline
from strawberry.types import Info

from nextlinegraphql.plugins.ctrl import example_script as example_script_module

EXAMPLE_SCRIPT_PATH = Path(example_script_module.__file__).parent / 'script.py'
assert EXAMPLE_SCRIPT_PATH.is_file()
example_script = EXAMPLE_SCRIPT_PATH.read_text()


async def mutate_exec(info: Info) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.run()
    return True


async def mutate_run_and_continue(info: Info) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.run_and_continue()
    return True


async def mutate_reset(info: Info, statement: Optional[str] = None) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.reset(statement=statement)
    return True


async def mutate_send_pdb_command(
    info: Info, command: str, prompt_no: int, trace_no: int
) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.send_pdb_command(command, prompt_no, trace_no)
    return True


async def mutate_interrupt(info: Info) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.interrupt()
    return True


async def mutate_terminate(info: Info) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.terminate()
    return True


async def mutate_kill(info: Info) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.kill()
    return True


async def mutate_load_example_script(info: Info) -> bool:
    nextline = info.context['nextline']
    assert isinstance(nextline, Nextline)
    await nextline.reset(statement=example_script)
    return True


@strawberry.type
class MutationCtrl:
    exec: bool = strawberry.field(resolver=mutate_exec)
    run_and_continue: bool = strawberry.field(resolver=mutate_run_and_continue)
    reset: bool = strawberry.field(resolver=mutate_reset)
    send_pdb_command: bool = strawberry.field(resolver=mutate_send_pdb_command)
    interrupt: bool = strawberry.field(resolver=mutate_interrupt)
    terminate: bool = strawberry.field(resolver=mutate_terminate)
    kill: bool = strawberry.field(resolver=mutate_kill)
    load_example_script: bool = strawberry.field(resolver=mutate_load_example_script)


@strawberry.type
class Mutation:
    @strawberry.field
    def ctrl(self) -> MutationCtrl:
        return MutationCtrl()
