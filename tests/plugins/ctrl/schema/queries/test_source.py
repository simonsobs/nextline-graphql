from pathlib import Path

import pytest
from nextline import Nextline
from syrupy.assertion import SnapshotAssertion

from nextlinegraphql.plugins.ctrl import example_script as example_script_module
from nextlinegraphql.plugins.ctrl.graphql import QUERY_SOURCE
from tests.plugins.ctrl.schema.conftest import Schema

EXAMPLE_SCRIPT_DIR = Path(example_script_module.__file__).resolve().parent
EXAMPLE_SCRIPT_PATH = EXAMPLE_SCRIPT_DIR / 'script.py'
example_script = EXAMPLE_SCRIPT_PATH.read_text()

SCRIPT_PATH = str(EXAMPLE_SCRIPT_DIR / 'script_threading.py')

params = [
    pytest.param(None, id='default'),
    pytest.param('<string>', id='string'),
    pytest.param(SCRIPT_PATH, id='path'),
]


@pytest.mark.parametrize('file_name', params)
async def test_schema(
    schema: Schema, snapshot: SnapshotAssertion, file_name: str | None
) -> None:
    nextline = Nextline(example_script, trace_modules=True, trace_threads=True)
    async with nextline:
        context = {'nextline': nextline}

        variables = {}
        if file_name:
            variables['fileName'] = file_name

        result = await schema.execute(
            QUERY_SOURCE, context_value=context, variable_values=variables
        )
        assert (data := result.data)

        snapshot.assert_match(data)
