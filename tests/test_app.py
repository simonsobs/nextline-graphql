"""Test the app object

The ASGI test client async-asgi-testclient is used
- https://pypi.org/project/async-asgi-testclient/
- https://github.com/vinissimus/async-asgi-testclient

"""

from async_asgi_testclient import TestClient

import pytest

from nextlinegraphql import app


##__________________________________________________________________||
@pytest.mark.asyncio
async def test_cors_get():
    """test if CORSMiddleware is in effect

    The response header should include CORSMiddleware
    "Access-Control-Allow-Origin: *" if the request header include the
    field "Origin."

    Useful links about CORS
    https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests
    https://gist.github.com/FND/204ba41bf6ae485965ef

    """

    headers = {
        "ORIGIN": "https://foo.example",
    }
    async with TestClient(app) as client:
        resp = await client.get("/", headers=headers)
        assert "*" == resp.headers["access-control-allow-origin"]
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_cors_preflight():
    """test if CORSMiddleware is in effect with the preflighted request

    https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#preflighted_requests
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS#preflighted_requests_in_cors
    """

    headers = {
        "ORIGIN": "https://foo.example",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-PINGOTHER, Content-Type",
    }
    async with TestClient(app) as client:
        resp = await client.options("/", headers=headers)
        assert "*" == resp.headers["access-control-allow-origin"]
        assert resp.status_code == 200


##__________________________________________________________________||
@pytest.mark.asyncio
async def test_playground():
    """test if the playground is returned for the get request"""
    async with TestClient(app) as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "text/html" in (resp.headers["content-type"].lower())
        assert "playground" in resp.text.lower()


##__________________________________________________________________||
