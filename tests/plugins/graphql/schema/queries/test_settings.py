import json

from nextlinegraphql.plugins.graphql.graphql import QUERY_SETTINGS
from nextlinegraphql.plugins.graphql.test import TestClient, gql_request


async def test_settings(client: TestClient):
    data = await gql_request(client, QUERY_SETTINGS)
    assert json.loads(data['settings'])
