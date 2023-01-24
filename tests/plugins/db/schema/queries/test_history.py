from async_asgi_testclient import TestClient

from nextlinegraphql.plugins.ctrl.test import run_statement
from nextlinegraphql.plugins.graphql.test import gql_request

from ..graphql import QUERY_HISTORY


async def test_one(client: TestClient):

    await run_statement(client)

    data = await gql_request(client, QUERY_HISTORY)
    # print(data["history"])
    runs = data["history"]["runs"]
    edges = runs["edges"]
    # assert 2 == len(runs)
    run = edges[1]["node"]
    assert 2 == run["runNo"]
    assert "finished" == run["state"]
    assert run["startedAt"]
    assert run["endedAt"]
    assert run["script"]
    assert not run["exception"]
