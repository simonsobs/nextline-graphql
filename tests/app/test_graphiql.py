"""Test the app object

The ASGI test client async-asgi-testclient is used
- https://pypi.org/project/async-asgi-testclient/
- https://github.com/vinissimus/async-asgi-testclient

"""

from async_asgi_testclient import TestClient

import pytest

from nextlinegraphql import create_app


@pytest.mark.asyncio
async def test_graphiql():
    """test if the graphiql is returned for the get request"""
    async with TestClient(create_app()) as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "text/html" in (resp.headers["content-type"].lower())
        assert "graphiql" in resp.text.lower()
