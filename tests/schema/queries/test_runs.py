import pytest
from async_asgi_testclient import TestClient

from ..funcs import gql_request
from ..graphql import QUERY_RUNS

from .funcs import run_statement

SOURCE = """
x = 1
""".strip()

# from pprint import pprint


@pytest.mark.asyncio
async def test_one(client: TestClient):

    statement = SOURCE
    await run_statement(client, statement)

    data = await gql_request(client, QUERY_RUNS)
    runs = data["runs"]
    assert 2 == len(runs)
    run = runs[1]
    assert 2 == run["runNo"]
    assert "finished" == run["state"]
    assert run["startedAt"]
    assert run["endedAt"]
    assert SOURCE == run["script"]
    assert not run["exception"]
