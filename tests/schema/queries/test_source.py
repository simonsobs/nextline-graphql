import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, Mock

from async_asgi_testclient import TestClient

from nextlinegraphql import app

from ..gql import (
    QUERY_SOURCE
)

##__________________________________________________________________||
THIS_DIR = Path(__file__).resolve().parent
PACKAGE_TOP = THIS_DIR.parent.parent.parent
SCRIPT_PATH = str(PACKAGE_TOP.joinpath('nextlinegraphql', 'schema', 'bindables', 'script_threading.py'))

params = [
    pytest.param(None, id='default'),
    pytest.param('<string>', id='string'),
    pytest.param(SCRIPT_PATH, id='path'),
]

@pytest.mark.parametrize('file_name', params)
@pytest.mark.asyncio
async def test_source(snapshot, file_name):

    data = { 'query': QUERY_SOURCE }

    if file_name:
        data['variables'] = { 'fileName': file_name }

    headers = {
        'Content-Type:': "application/json"
    }

    async with TestClient(app) as client:
        resp = await client.post("/", json=data, headers=headers)
        assert resp.status_code == 200
        snapshot.assert_match(resp.json())

##__________________________________________________________________||
