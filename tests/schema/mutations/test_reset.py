import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, Mock

from async_asgi_testclient import TestClient

from nextlinegraphql import app

from ..gql import (
    QUERY_SOURCE,
    MUTATION_RESET
)

##__________________________________________________________________||
SOURCE_ONE = """
import time
time.sleep(0.1)
""".strip()

##__________________________________________________________________||
params = [
    pytest.param(None, id='no-statement'),
    pytest.param(SOURCE_ONE, id='statement'),
]

@pytest.mark.parametrize('statement', params)
@pytest.mark.asyncio
async def test_reset(snapshot, statement):

    headers = {
        'Content-Type:': "application/json"
    }

    data = { 'query': MUTATION_RESET }
    if statement:
        data['variables'] = { 'statement': statement }

    async with TestClient(app) as client:
        resp = await client.post("/", json=data, headers=headers)
        assert resp.status_code == 200
        assert {'data': {'reset': True}} == resp.json()

    data = { 'query': QUERY_SOURCE }

    async with TestClient(app) as client:
        resp = await client.post("/", json=data, headers=headers)
        assert resp.status_code == 200
        snapshot.assert_match(resp.json())

##__________________________________________________________________||
