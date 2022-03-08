from pathlib import Path

import pytest

from async_asgi_testclient import TestClient

from nextlinegraphql import create_app

from ..graphql import QUERY_SOURCE
from ..funcs import gql_request

##__________________________________________________________________||
THIS_DIR = Path(__file__).resolve().parent
PACKAGE_TOP = THIS_DIR.parent.parent.parent
SCRIPT_PATH = str(
    PACKAGE_TOP.joinpath(
        "nextlinegraphql", "example_script", "script_threading.py"
    )
)

params = [
    pytest.param(None, id="default"),
    pytest.param("<string>", id="string"),
    pytest.param(SCRIPT_PATH, id="path"),
]


@pytest.fixture
async def client():
    async with TestClient(create_app()) as y:
        yield y


@pytest.mark.parametrize("file_name", params)
@pytest.mark.asyncio
async def test_source(client: TestClient, snapshot, file_name):

    variables = {}
    if file_name:
        variables["fileName"] = file_name

    data = await gql_request(client, QUERY_SOURCE, variables=variables)
    snapshot.assert_match(data)


##__________________________________________________________________||
