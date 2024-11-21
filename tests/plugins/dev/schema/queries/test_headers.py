import json
from unittest.mock import Mock

from starlette.requests import Headers, Request

from nextlinegraphql.plugins.dev.graphql import QUERY_HEADERS
from tests.plugins.dev.schema.conftest import Schema


async def test_schema(schema: Schema) -> None:
    request = Mock(spec=Request)
    request.headers = Headers({'foo': 'bar'})
    context = {'request': request}
    result = await schema.execute(QUERY_HEADERS, context_value=context)
    assert (data := result.data)
    expected = {'dev': {'headers': json.dumps({'foo': 'bar'})}}
    assert data == expected

