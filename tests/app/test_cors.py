from async_asgi_testclient import TestClient


async def test_get(client: TestClient):
    '''test if CORSMiddleware is in effect

    The response header should include CORSMiddleware
    'Access-Control-Allow-Origin: *' if the request header include the
    field 'Origin.'

    Useful links about CORS
    https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests
    https://gist.github.com/FND/204ba41bf6ae485965ef

    '''

    headers = {
        'ORIGIN': 'https://foo.example',
        'Accept': 'text/html',
    }

    resp = await client.get('/', headers=headers)
    assert '*' == resp.headers['access-control-allow-origin']
    assert resp.status_code == 200


async def test_preflight(client: TestClient):
    '''test if CORSMiddleware is in effect with the preflighted request

    https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#preflighted_requests
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS#preflighted_requests_in_cors
    '''

    headers = {
        'ORIGIN': 'https://foo.example',
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'X-PINGOTHER, Content-Type',
    }

    resp = await client.options('/', headers=headers)
    assert '*' == resp.headers['access-control-allow-origin']
    assert resp.status_code == 200
