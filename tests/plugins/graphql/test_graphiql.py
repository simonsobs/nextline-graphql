from nextlinegraphql.plugins.graphql.test import TestClient


async def test_one(client: TestClient) -> None:
    '''Assert GraphQL IDE for the HTTP get request'''
    headers = {'Accept': 'text/html'}
    resp = await client.get('/', headers=headers)
    assert resp.status_code == 200
    assert 'text/html' in resp.headers['content-type'].lower()
    assert 'graphiql' in resp.text.lower()
