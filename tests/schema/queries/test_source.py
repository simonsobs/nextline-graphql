from pathlib import Path

import pytest

from async_asgi_testclient import TestClient

from ..graphql import QUERY_SOURCE
from ..funcs import gql_request

CWD = Path(__file__).resolve().parent
PACKAGE_TOP = CWD.parent.parent.parent
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


@pytest.mark.parametrize("file_name", params)
async def test_source(client: TestClient, snapshot, file_name):

    variables = {}
    if file_name:
        variables["fileName"] = file_name

    data = await gql_request(client, QUERY_SOURCE, variables=variables)
    snapshot.assert_match(data)
