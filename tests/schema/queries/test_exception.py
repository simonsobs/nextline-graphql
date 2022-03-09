import asyncio

import pytest

from async_asgi_testclient import TestClient

from nextlinegraphql import create_app

from ..graphql import (
    QUERY_STATE,
    QUERY_SOURCE_LINE,
    QUERY_EXCEPTION,
    SUBSCRIBE_STATE,
    SUBSCRIBE_TRACE_IDS,
    SUBSCRIBE_PROMPTING,
    MUTATE_EXEC,
    MUTATE_RESET,
    MUTATE_SEND_PDB_COMMAND,
)

##__________________________________________________________________||
SOURCE_ONE = """
import time
time.sleep(0.1)
""".strip()

SOURCE_RAISE = """
raise Exception('foo', 'bar')
""".strip()


##__________________________________________________________________||
async def control_trace(client, trace_id):
    # print(f'control_trace({trace_id})')

    to_step = []

    subscribe_thread_task_state = {
        "id": "1",
        "type": "start",
        "payload": {
            "variables": {"traceId": trace_id},
            "extensions": {},
            "operationName": None,
            "query": SUBSCRIBE_PROMPTING,
        },
    }

    query_source_line = {"query": QUERY_SOURCE_LINE}

    mutate_send_pdb_command = {"query": MUTATE_SEND_PDB_COMMAND}

    headers = {"Content-Type:": "application/json"}

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_thread_task_state)
        while True:
            resp_json = await ws.receive_json()
            if resp_json["type"] == "complete":
                break
            assert "errors" not in resp_json["payload"]
            state = resp_json["payload"]["data"]["prompting"]
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


async def control_execution(client):

    subscribe_thread_task_ids = {
        "id": "1",
        "type": "start",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": None,
            "query": SUBSCRIBE_TRACE_IDS,
        },
    }

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_thread_task_ids)
        prev_ids = set()
        tasks_control_thread_task = set()
        task_receive_json = asyncio.create_task(ws.receive_json())
        while True:
            aws = {task_receive_json, *tasks_control_thread_task}
            done, pending = await asyncio.wait(
                aws, return_when=asyncio.FIRST_COMPLETED
            )
            results = [
                t.result() for t in tasks_control_thread_task & done
            ]  # raise exception
            tasks_control_thread_task = tasks_control_thread_task & pending
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
                tasks_control_thread_task.add(task)
            prev_ids = ids


async def monitor_state(client):

    subscribe_state = {
        "id": "1",
        "type": "start",
        "payload": {
            "variables": {},
            "extensions": {},
            "operationName": None,
            "query": SUBSCRIBE_STATE,
        },
    }

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_state)
        while True:
            resp_json = await ws.receive_json()
            if resp_json["type"] == "complete":
                break
            # print(resp_json['payload']['data']['state'])
            if resp_json["payload"]["data"]["state"] == "finished":
                break


##__________________________________________________________________||
params = [
    pytest.param(SOURCE_ONE, id="not-raise"),
    pytest.param(SOURCE_RAISE, id="raise"),
]


@pytest.mark.parametrize("statement", params)
@pytest.mark.asyncio
async def test_reset(snapshot, statement):

    headers = {"Content-Type:": "application/json"}

    query_state = {"query": QUERY_STATE}

    query_exception = {"query": QUERY_EXCEPTION}

    mutate_reset = {
        "query": MUTATE_RESET,
        "variables": {"statement": statement},
    }

    mutate_exec = {"query": MUTATE_EXEC}

    async with TestClient(create_app()) as client:
        resp = await client.post("/", json=mutate_reset, headers=headers)
        assert resp.status_code == 200
        assert {"data": {"reset": True}} == resp.json()

        resp = await client.post("/", json=query_state, headers=headers)
        assert resp.status_code == 200
        assert "initialized" == resp.json()["data"]["state"]

        task_monitor_state = asyncio.create_task(
            monitor_state(client)
        )

        resp = await client.post("/", json=mutate_exec, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["exec"]

        task_control_execution = asyncio.create_task(control_execution(client))

        aws = {task_monitor_state, task_control_execution}
        while aws:
            done, pending = await asyncio.wait(
                aws, return_when=asyncio.FIRST_COMPLETED
            )
            results = [t.result() for t in done]  # re-raise exception
            aws = pending
            # break

        resp = await client.post("/", json=query_exception, headers=headers)
        assert resp.status_code == 200
        resp.json()["data"]["exception"]


##__________________________________________________________________||
