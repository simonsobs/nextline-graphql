from async_asgi_testclient import TestClient

from ....ctrl.schema.funcs import gql_request
from ....ctrl.schema.queries.funcs import run_statement
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
