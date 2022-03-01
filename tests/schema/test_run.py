import asyncio
from async_asgi_testclient import TestClient

import pytest

from typing import Set, Dict, Any, TypedDict

from nextlinegraphql import create_app

from .gql import (
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


async def control_trace(client: TestClient, trace_id: int) -> None:
    # print(f'control_trace({trace_id})')

    to_step = ["script_threading.run()", "script_asyncio.run()"]

    subscribe_trace_state = SubscribeMessage(
        id="1",
        type="start",
        payload=SubscribePayload(
            variables={"traceId": trace_id},
            extensions={},
            operationName=None,
            query=SUBSCRIBE_TRACE_STATE,
        ),
    )

    query_source_line = PostRequest(query=QUERY_SOURCE_LINE)

    mutate_send_pdb_command = PostRequest(query=MUTATE_SEND_PDB_COMMAND)

    headers = {"Content-Type:": "application/json"}

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_trace_state)
        while True:
            resp_json = await ws.receive_json()
            if resp_json["type"] == "complete":
                break
            assert "errors" not in resp_json["payload"]
            state = resp_json["payload"]["data"]["traceState"]
            # print(state)
            if state["prompting"]:
                command = "next"
                if state["traceEvent"] == "line":
                    query_source_line["variables"] = {
                        "lineNo": state["lineNo"],
                        "fileName": state["fileName"],
                    }
                    resp = await client.post(
                        "/", json=query_source_line, headers=headers
                    )
                    source_line = resp.json()["data"]["sourceLine"]

                    # print(source_line)
                    # print(source_line in to_step)
                    if source_line in to_step:
                        command = "step"

                mutate_send_pdb_command["variables"] = {
                    "traceId": trace_id,
                    "command": command,
                }
                resp = await client.post(
                    "/", json=mutate_send_pdb_command, headers=headers
                )
                # print(resp.json())


async def control_execution(client: TestClient):

    subscribe_trace_ids = SubscribeMessage(
        id="1",
        type="start",
        payload=SubscribePayload(
            variables={},
            extensions={},
            operationName=None,
            query=SUBSCRIBE_TRACE_IDS,
        ),
    )

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_trace_ids)
        prev_ids: Set[int] = set()
        tasks_control_trace: Set[asyncio.Task] = set()
        task_receive_json = asyncio.create_task(ws.receive_json())
        while True:
            aws = {task_receive_json, *tasks_control_trace}
            done, pending = await asyncio.wait(
                aws, return_when=asyncio.FIRST_COMPLETED
            )
            _ = [
                t.result() for t in tasks_control_trace & done
            ]  # raise exception
            tasks_control_trace = tasks_control_trace & pending
            if task_receive_json not in done:
                continue
            resp_json = task_receive_json.result()
            task_receive_json = asyncio.create_task(ws.receive_json())
            # print(resp_json)
            if resp_json["type"] == "complete":
                break
            ids = resp_json["payload"]["data"]["traceIds"]  # a list of dicts
            if not ids:
                break
            ids = set(ids)
            new_ids = ids - prev_ids
            for id_ in new_ids:
                task = asyncio.create_task(control_trace(client, id_))
                tasks_control_trace.add(task)
            prev_ids = ids


async def monitor_state(client: TestClient) -> None:

    subscribe_state = SubscribeMessage(
        id="1",
        type="start",
        payload=SubscribePayload(
            variables={},
            extensions={},
            operationName=None,
            query=SUBSCRIBE_GLOBAL_STATE,
        ),
    )

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_state)
        while True:
            resp_json = await ws.receive_json()
            if resp_json["type"] == "complete":
                break
            # print(resp_json['payload']['data']['globalState'])
            if resp_json["payload"]["data"]["globalState"] == "finished":
                break


@pytest.mark.asyncio
async def test_run():

    query_state = PostRequest(query=QUERY_GLOBAL_STATE)

    mutate_exec = PostRequest(query=MUTATE_EXEC)

    headers = {"Content-Type:": "application/json"}

    async with TestClient(create_app()) as client:
        resp = await client.post("/", json=query_state, headers=headers)
        assert "initialized" == resp.json()["data"]["globalState"]

        task_monitor_state = asyncio.create_task(monitor_state(client))

        resp = await client.post("/", json=mutate_exec, headers=headers)
        assert resp.json()["data"]["exec"]

        task_control_execution = asyncio.create_task(control_execution(client))

        aws = {task_monitor_state, task_control_execution}
        while aws:
            done, pending = await asyncio.wait(
                aws, return_when=asyncio.FIRST_COMPLETED
            )
            _ = [t.result() for t in done]  # re-raise exception
            aws = pending
            # break # to be removed

        resp = await client.post("/", json=query_state, headers=headers)
        assert "finished" == resp.json()["data"]["globalState"]


##__________________________________________________________________||
