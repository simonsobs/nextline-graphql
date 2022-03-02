import asyncio
from async_asgi_testclient import TestClient

import pytest

from typing import AsyncGenerator, Optional, Set, Dict, Any, TypedDict

from nextlinegraphql import create_app

from .gql_strs import (
    QUERY_GLOBAL_STATE,
    QUERY_SOURCE_LINE,
    SUBSCRIBE_GLOBAL_STATE,
    SUBSCRIBE_TRACE_IDS,
    SUBSCRIBE_TRACE_STATE,
    MUTATE_EXEC,
    MUTATE_SEND_PDB_COMMAND,
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


async def control_trace(client: TestClient, trace_id: int) -> None:
    # print(f'control_trace({trace_id})')

    to_step = ["script_threading.run()", "script_asyncio.run()"]

    async for data in gql_subscribe(
        client,
        SUBSCRIBE_TRACE_STATE,
        variables={"traceId": trace_id},
    ):
        state = data["traceState"]
        # print(state)
        if state["prompting"]:
            command = "next"
            if state["traceEvent"] == "line":
                data = await gql_request(
                    client,
                    QUERY_SOURCE_LINE,
                    variables={
                        "lineNo": state["lineNo"],
                        "fileName": state["fileName"],
                    },
                )
                source_line = data["sourceLine"]

                # print(source_line)
                # print(source_line in to_step)
                if source_line in to_step:
                    command = "step"

            data = await gql_request(
                client,
                MUTATE_SEND_PDB_COMMAND,
                variables={
                    "traceId": trace_id,
                    "command": command,
                },
            )
            assert data["sendPdbCommand"]


async def agen_with_wait(
    agen: AsyncGenerator,
) -> AsyncGenerator[Any, Set[asyncio.Task]]:
    """Yield from the agen while waiting for received tasks

    Used to raise an exception from tasks
    """
    tasks: Set[asyncio.Task] = set()
    task_anext = asyncio.create_task(agen.__anext__())
    while True:
        done, pending = await asyncio.wait(
            tasks | {task_anext}, return_when=asyncio.FIRST_COMPLETED
        )
        for t in done:
            if exc := t.exception():
                raise exc
        tasks &= pending
        if task_anext not in done:
            continue
        try:
            data = task_anext.result()
        except StopAsyncIteration:
            break
        tasks |= yield data
        yield
        task_anext = asyncio.create_task(agen.__anext__())


async def control_execution(client: TestClient):

    agen = agen_with_wait(gql_subscribe(client, SUBSCRIBE_TRACE_IDS))

    prev_ids: Set[int] = set()
    async for data in agen:
        if not (ids := set(data["traceIds"])):
            break
        new_ids, prev_ids = ids - prev_ids, ids
        tasks = {
            asyncio.create_task(
                control_trace(client, id_),
            )
            for id_ in new_ids
        }
        await agen.asend(tasks)


async def monitor_state(client: TestClient) -> None:

    async for data in gql_subscribe(client, SUBSCRIBE_GLOBAL_STATE):
        # print(data)
        if data["globalState"] == "finished":
            break


@pytest.mark.asyncio
async def test_run():

    async with TestClient(create_app()) as client:
        data = await gql_request(client, QUERY_GLOBAL_STATE)
        assert "initialized" == data["globalState"]

        task_monitor_state = asyncio.create_task(monitor_state(client))

        data = await gql_request(client, MUTATE_EXEC)
        assert data["exec"]

        await asyncio.sleep(0.01)

        task_control_execution = asyncio.create_task(control_execution(client))

        await asyncio.gather(task_monitor_state, task_control_execution)

        data = await gql_request(client, QUERY_GLOBAL_STATE)
        assert "finished" == data["globalState"]
