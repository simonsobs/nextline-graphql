import json

from strawberry import Schema

from nextlinegraphql.config import load_settings
from nextlinegraphql.hook import load_plugins
from nextlinegraphql.plugins.graphql.graphql import QUERY_SETTINGS
from nextlinegraphql.plugins.graphql.schema import Query


async def test_settings() -> None:
    schema = Schema(query=Query)
    hook = load_plugins()
    settings = load_settings(hook)
    context = {'settings': settings}
    result = await schema.execute(QUERY_SETTINGS, context_value=context)
    assert not result.errors
    assert result.data
    assert result.data['settings']
    assert json.dumps(settings.to_dict()) == result.data['settings']
