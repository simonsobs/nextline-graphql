from nextline import Nextline
from strawberry import Schema

from nextlinegraphql.plugins.ctrl.graphql import QUERY_EXCEPTION
from nextlinegraphql.plugins.ctrl.schema import Mutation, Query, Subscription

SOURCE_RAISE = '''
raise Exception('foo', 'bar')
'''.strip()


async def test_schema() -> None:
    schema = Schema(query=Query, mutation=Mutation, subscription=Subscription)
    assert schema
    nextline = Nextline(SOURCE_RAISE, trace_modules=True, trace_threads=True)
    async with nextline:
        context = {'nextline': nextline}

        await nextline.run_continue_and_wait()

        result = await schema.execute(QUERY_EXCEPTION, context_value=context)
        assert (data := result.data)

        assert "Exception: ('foo', 'bar')" in data['exception']
