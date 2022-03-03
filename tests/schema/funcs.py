import asyncio
from async_asgi_testclient import TestClient


from typing import (
    AsyncGenerator,
    Iterable,
    Optional,
    Set,
    Dict,
    Any,
    TypedDict,
)


class PostRequest(TypedDict, total=False):
    """GraphQL POST Request
    https://graphql.org/learn/serving-over-http/#post-request
    """

    query: str
    variables: Dict[str, Any]
    operationName: str


class SubscribePayload(TypedDict):
    variables: Dict[str, Any]
    extensions: Dict[str, Any]
    operationName: Any
    query: str


class SubscribeMessage(TypedDict):
    """GraphQL over WebSocket Protocol

    The type of the payload might depend on the value of the type.
    SubscribePayload might be only for the type "start".
    https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md#subscribe
    https://github.com/enisdenjo/graphql-ws/blob/master/PROTOCOL.md
    """

    id: str
    type: str
    payload: SubscribePayload


async def gql_request(
    client: TestClient,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
) -> Any:

    request = PostRequest(query=query)
    if variables:
        request["variables"] = variables

    headers = {"Content-Type:": "application/json"}

    resp = await client.post("/", json=request, headers=headers)
    return resp.json()["data"]


async def gql_subscribe(
    client: TestClient,
    query: str,
    variables: Optional[Dict[str, Any]] = None,
) -> AsyncGenerator[Any, None]:

    payload = SubscribePayload(
        variables=variables if variables else {},
        extensions={},
        operationName=None,
        query=query,
    )

    message = SubscribeMessage(id="1", type="start", payload=payload)

    async with client.websocket_connect("/") as ws:
        await ws.send_json(message)
        while True:
            resp_json = await ws.receive_json()
            if resp_json["type"] == "complete":
                break
            yield resp_json["payload"]["data"]


async def agen_with_wait(
    agen: AsyncGenerator,
) -> AsyncGenerator[Any, Iterable[asyncio.Task]]:
    """Yield from the agen while waiting for received tasks

    Used to raise an exception from tasks
    """
    done: Set[asyncio.Task] = set()
    pending: Set[asyncio.Task] = set()
    anext = asyncio.create_task(agen.__anext__())
    while True:
        done_, pending_ = await asyncio.wait(
            pending | {anext}, return_when=asyncio.FIRST_COMPLETED
        )
        for t in done_ - {anext}:
            if exc := t.exception():
                raise exc
        if anext in done_:
            try:
                data = anext.result()
            except StopAsyncIteration:
                break
            done_.remove(anext)
            done |= done_
        else:
            done |= done_
            continue
        pending &= pending_
        new = yield data
        pending |= set(new)
        yield tuple(done), tuple(pending)
        done.clear()
        anext = asyncio.create_task(agen.__anext__())
