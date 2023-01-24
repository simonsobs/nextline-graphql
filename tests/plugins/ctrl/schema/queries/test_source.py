from pathlib import Path

import pytest
from async_asgi_testclient import TestClient

from nextlinegraphql.plugins.ctrl import example_script
from nextlinegraphql.plugins.graphql.test import gql_request

from ..graphql import QUERY_SOURCE

EXAMPLE_SCRIPT_DIR = Path(example_script.__file__).resolve().parent
SCRIPT_PATH = str(EXAMPLE_SCRIPT_DIR / 'script_threading.py')

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
