import asyncio

from nextline import Nextline
from strawberry.types import ExecutionResult

from nextlinegraphql.plugins.ctrl.graphql import MUTATE_INTERRUPT
from tests.plugins.ctrl.schema.conftest import Schema

SOURCE = '''
import time
time.sleep(5)
'''.strip()


async def test_schema(schema: Schema) -> None:
    nextline = Nextline(SOURCE, trace_modules=True, trace_threads=True)
    started = asyncio.Event()
    context = {'nextline': nextline}
    async with nextline:
        task = asyncio.create_task(nextline.run_continue_and_wait(started=started))

        await started.wait()  # TODO: Update `started` so that `sleep()` is unnecessary
        await asyncio.sleep(1)

        result = await schema.execute(MUTATE_INTERRUPT, context_value=context)

        assert isinstance(result, ExecutionResult)
        assert (data := result.data)
        assert data['ctrl']['interrupt'] is True

        await task
        assert (exc := nextline.format_exception()) is not None
        assert 'KeyboardInterrupt' in exc
