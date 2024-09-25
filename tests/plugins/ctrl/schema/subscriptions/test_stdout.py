import asyncio
from typing import Any

from nextline import Nextline
from nextlinegraphql.plugins.ctrl.cache import CacheStdout
from nextlinegraphql.plugins.ctrl.graphql import SUBSCRIBE_STDOUT
from tests.plugins.ctrl.schema.conftest import Schema

SOURCE = '''
import time
for i in range(10):
    print(i)
    time.sleep(0.005)
'''.strip()


async def test_schema(schema: Schema) -> None:
    nextline = Nextline(SOURCE, trace_modules=True, trace_threads=True)
    cache_stdout = CacheStdout()
    nextline.register(cache_stdout)
    started = asyncio.Event()
    context = {'nextline': nextline, 'ctrl': {'cache_stdout': cache_stdout}}
    async with cache_stdout, nextline:
        task = asyncio.create_task(nextline.run_continue_and_wait(started=started))
        await started.wait()
        sub = asyncio.create_task(_subscribe_stdout(schema, context=context))
        await task
        await nextline.reset()
        await asyncio.create_task(nextline.run_continue_and_wait(started=started))

    stdout = await sub
    assert stdout == '0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n' '0\n1\n2\n3\n4\n5\n6\n7\n8\n9\n'


async def _subscribe_stdout(schema: Schema, context: Any) -> str:
    sub = await schema.subscribe(SUBSCRIBE_STDOUT, context_value=context)
    assert hasattr(sub, '__aiter__')
    ret = ''
    async for result in sub:
        assert (data := result.data)
        ret += data['ctrlStdout']
    return ret
