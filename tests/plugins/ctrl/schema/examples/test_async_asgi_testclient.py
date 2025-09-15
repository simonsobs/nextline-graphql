from nextlinegraphql import create_app
from nextlinegraphql.plugins.graphql.test import TestClient


async def test_query() -> None:
    query = '''
      { ctrl
        { hello }
      }
    '''
    data = {'query': query}

    headers = {
        'user-agent': 'Mozilla/5.0',
        'Content-Type:': 'application/json',
    }

    async with TestClient(create_app(enable_external_plugins=False)) as client:
        resp = await client.post('/', json=data, headers=headers)
        assert resp.status_code == 200
        expect = {'data': {'ctrl': {'hello': 'Hello, Mozilla/5.0!'}}}
        assert expect == resp.json()


async def test_subscription() -> None:
    query = '''
      subscription {
        ctrlCounter
      }
    '''

    data = {
        'id': '1',
        'type': 'start',
        'payload': {
            'variables': {},
            'extensions': {},
            'operationName': None,
            'query': query,
        },
    }

    async with TestClient(create_app(enable_external_plugins=False)) as client:
        async with client.websocket_connect('/') as ws:
            await ws.send_json(data)

            expect = {
                'type': 'data',
                'id': '1',
                'payload': {'data': {'ctrlCounter': 1}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                'type': 'data',
                'id': '1',
                'payload': {'data': {'ctrlCounter': 2}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                'type': 'data',
                'id': '1',
                'payload': {'data': {'ctrlCounter': 3}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                'type': 'data',
                'id': '1',
                'payload': {'data': {'ctrlCounter': 4}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                'type': 'data',
                'id': '1',
                'payload': {'data': {'ctrlCounter': 5}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {'type': 'complete', 'id': '1'}
            actual = await ws.receive_json()
            assert expect == actual
