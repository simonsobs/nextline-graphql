import json

from dynaconf import Dynaconf
from strawberry import Schema

from nextlinegraphql.plugins.graphql.graphql import QUERY_SETTINGS
from nextlinegraphql.plugins.graphql.schema import Query


async def test_settings() -> None:
    schema = Schema(query=Query)
    settings = {'FOO': 'bar'}
    conf = Dynaconf(**settings)
    context = {'settings': conf}
    result = await schema.execute(QUERY_SETTINGS, context_value=context)
    assert not result.errors
    assert result.data
    assert result.data['settings']
    assert settings == json.loads(result.data['settings'])
