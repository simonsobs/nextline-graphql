import pytest
from async_asgi_testclient import TestClient


@pytest.mark.asyncio
async def test_one(client: TestClient):
    """Assert GraphQL IDE for the HTTP get request"""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"].lower()
    assert "graphiql" in resp.text.lower()