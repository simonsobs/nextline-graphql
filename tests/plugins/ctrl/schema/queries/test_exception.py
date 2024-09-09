from nextline import Nextline
from strawberry.types import ExecutionResult

from nextlinegraphql.plugins.ctrl.graphql import QUERY_EXCEPTION
from tests.plugins.ctrl.schema.conftest import Schema

SOURCE_RAISE = '''
raise Exception('foo', 'bar')
'''.strip()


async def test_schema(schema: Schema) -> None:
    nextline = Nextline(SOURCE_RAISE, trace_modules=True, trace_threads=True)
    async with nextline:
        context = {'nextline': nextline}

        await nextline.run_continue_and_wait()

        result = await schema.execute(QUERY_EXCEPTION, context_value=context)
        assert isinstance(result, ExecutionResult)
        assert (data := result.data)

        assert "Exception: ('foo', 'bar')" in data['ctrl']['exception']
