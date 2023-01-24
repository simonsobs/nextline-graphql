from async_asgi_testclient import TestClient

from nextlinegraphql.plugins.graphql.test import gql_request

from ..graphql import QUERY_EXCEPTION
from .funcs import run_statement

SOURCE_RAISE = """
raise Exception('foo', 'bar')
""".strip()


async def test_one(client: TestClient):

    statement = SOURCE_RAISE
    await run_statement(client, statement)

    data = await gql_request(client, QUERY_EXCEPTION)
    assert "('foo', 'bar')" in data["exception"]
