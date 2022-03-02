import asyncio
from async_asgi_testclient import TestClient

import pytest

from typing import Set

from nextlinegraphql import create_app

from .funcs import gql_request, gql_subscribe, agen_with_wait

from .gql_strs import (
    QUERY_GLOBAL_STATE,
    QUERY_SOURCE_LINE,
    SUBSCRIBE_GLOBAL_STATE,
    SUBSCRIBE_TRACE_IDS,
    SUBSCRIBE_TRACE_STATE,
    MUTATE_EXEC,
    MUTATE_SEND_PDB_COMMAND,
)


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
