from async_asgi_testclient import TestClient

from nextlinegraphql import create_app


##__________________________________________________________________||
async def test_query():
    query = """
      { hello }
    """
    data = {"query": query}

    headers = {
        "user-agent": "Mozilla/5.0",
        "Content-Type:": "application/json",
    }

    async with TestClient(create_app()) as client:
        resp = await client.post("/", json=data, headers=headers)
        assert resp.status_code == 200
        expect = {"data": {"hello": "Hello, Mozilla/5.0!"}}
        assert expect == resp.json()


##__________________________________________________________________||
async def test_subscription():
    query = """
      subscription {
        counter
      }
    """

    data = {
        "id": "1",
        "type": "start",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": None,
            "query": query,
        },
    }

    async with TestClient(create_app()) as client:
        async with client.websocket_connect("/") as ws:
            await ws.send_json(data)

            expect = {
                "type": "data",
                "id": "1",
                "payload": {"data": {"counter": 1}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                "type": "data",
                "id": "1",
                "payload": {"data": {"counter": 2}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                "type": "data",
                "id": "1",
                "payload": {"data": {"counter": 3}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                "type": "data",
                "id": "1",
                "payload": {"data": {"counter": 4}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {
                "type": "data",
                "id": "1",
                "payload": {"data": {"counter": 5}},
            }
            actual = await ws.receive_json()
            assert expect == actual

            expect = {"type": "complete", "id": "1"}
            actual = await ws.receive_json()
            assert expect == actual


##__________________________________________________________________||
