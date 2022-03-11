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
