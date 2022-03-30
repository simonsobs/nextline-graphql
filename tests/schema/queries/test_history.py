import pytest
from async_asgi_testclient import TestClient

from ..funcs import gql_request
from ..graphql import QUERY_HISTORY

from .funcs import run_statement


@pytest.mark.asyncio
async def test_one(client: TestClient):

    await run_statement(client)

    data = await gql_request(client, QUERY_HISTORY)
    # print(data["history"])
    runs = data["history"]["runs"]
    edges = runs["edges"]
    # assert 2 == len(runs)
    run = edges[0]["node"]
    assert 2 == run["runNo"]
    assert "finished" == run["state"]
    assert run["startedAt"]
    assert run["endedAt"]
    assert run["script"]
    assert not run["exception"]
