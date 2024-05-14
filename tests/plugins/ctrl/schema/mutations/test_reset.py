from pathlib import Path

import pytest
from nextline import Nextline
from strawberry import Schema

from nextlinegraphql.plugins.ctrl import example_script as example_script_module
from nextlinegraphql.plugins.ctrl.graphql import MUTATE_RESET, QUERY_SOURCE
from nextlinegraphql.plugins.ctrl.schema import Mutation, Query, Subscription

EXAMPLE_SCRIPT_PATH = Path(example_script_module.__file__).parent / 'script.py'
example_script = EXAMPLE_SCRIPT_PATH.read_text()

SOURCE_ONE = '''
import time
time.sleep(0.1)
'''.strip()

params = [
    pytest.param(None, id='no-statement'),
    pytest.param(SOURCE_ONE, id='statement'),
]


@pytest.mark.parametrize('statement', params)
async def test_schema(statement: str | None) -> None:
    schema = Schema(query=Query, mutation=Mutation, subscription=Subscription)
    assert schema
    nextline = Nextline(example_script, trace_modules=True, trace_threads=True)
    async with nextline:
        context = {'nextline': nextline}
        variables = {'statement': statement}
        result = await schema.execute(
            MUTATE_RESET, context_value=context, variable_values=variables
        )
        assert (data := result.data)
        assert data['ctrl']['reset'] is True

        result = await schema.execute(QUERY_SOURCE, context_value=context)
        assert (data := result.data)

        expected = statement or example_script
        assert expected.split('\n') == data['ctrl']['source']
