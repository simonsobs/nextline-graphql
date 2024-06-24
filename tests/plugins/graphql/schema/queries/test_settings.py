import json

from dynaconf import Dynaconf

from nextlinegraphql.plugins.graphql.graphql import QUERY_SETTINGS
from tests.plugins.graphql.schema.conftest import Schema


async def test_settings(schema: Schema) -> None:
    settings = {'FOO': 'bar'}
    conf = Dynaconf(**settings)
    context = {'settings': conf}
    result = await schema.execute(QUERY_SETTINGS, context_value=context)
    assert not result.errors
    assert result.data
    assert result.data['settings']
    assert settings == json.loads(result.data['settings'])
