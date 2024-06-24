import asyncio

from nextline import Nextline

from nextlinegraphql.plugins.ctrl.graphql import MUTATE_TERMINATE
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

        await started.wait()
        result = await schema.execute(MUTATE_TERMINATE, context_value=context)

        assert (data := result.data)
        assert data['ctrl']['terminate'] is True

        await task
        # TODO: Assert the exit code
