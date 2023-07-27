import asyncio

import strawberry
from nextline import Nextline
from strawberry.types import Info

from nextlinegraphql.plugins.continuous.types import ContinuousInfo


async def mutate_run_and_continue(info: Info) -> bool:
    nextline: Nextline = info.context['nextline']
    continuous_info: ContinuousInfo = info.context['continuous_info']
    task = asyncio.create_task(_run_and_continue(nextline, continuous_info))
    continuous_info.tasks.add(task)
    return True


@strawberry.type
class MutationContinuous:
    run_and_continue: bool = strawberry.field(resolver=mutate_run_and_continue)


@strawberry.type
class Mutation:
    @strawberry.field
    def continuous(self, info: Info) -> MutationContinuous:
        return MutationContinuous()


async def _run_and_continue(
    nextline: Nextline, continuous_info: ContinuousInfo
) -> None:
    await continuous_info.pubsub_enabled.publish(True)
    try:
        async with nextline.run_session():
            async for prompt in nextline.prompts():
                await nextline.send_pdb_command(
                    command='continue',
                    prompt_no=prompt.prompt_no,
                    trace_no=prompt.trace_no,
                )
    finally:
        await continuous_info.pubsub_enabled.publish(False)
