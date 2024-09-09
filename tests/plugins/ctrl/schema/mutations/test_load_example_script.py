from pathlib import Path

from nextline import Nextline
from strawberry.types import ExecutionResult

from nextlinegraphql.plugins.ctrl import example_script as example_script_module
from nextlinegraphql.plugins.ctrl.graphql import MUTATE_LOAD_EXAMPLE_SCRIPT
from tests.plugins.ctrl.schema.conftest import Schema

EXAMPLE_SCRIPT_PATH = Path(example_script_module.__file__).parent / 'script.py'
example_script = EXAMPLE_SCRIPT_PATH.read_text()

INITIAL_SCRIPT = '''
import time
time.sleep(0.001)
'''.strip()


async def test_query(schema: Schema) -> None:
    nextline = Nextline(INITIAL_SCRIPT)
    async with nextline:
        context = {'nextline': nextline}
        result = await schema.execute(MUTATE_LOAD_EXAMPLE_SCRIPT, context_value=context)
        assert isinstance(result, ExecutionResult)
        assert not result.errors
        assert result.data
        assert result.data['ctrl']['loadExampleScript'] is True
        assert nextline.statement == example_script
