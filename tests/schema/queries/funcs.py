import asyncio
from typing import List, Optional, Set
from async_asgi_testclient import TestClient

from nextline.utils import agen_with_wait

from ..funcs import gql_request, gql_subscribe

from ..graphql import (
    QUERY_STATE,
    SUBSCRIBE_STATE,
    SUBSCRIBE_TRACE_IDS,
    SUBSCRIBE_PROMPTING,
    MUTATE_RESET,
    MUTATE_EXEC,
    MUTATE_SEND_PDB_COMMAND,
)


async def run_statement(client, statement: Optional[str] = None):
    variables = {"statement": statement}
    data = await gql_request(client, MUTATE_RESET, variables=variables)
    assert data["reset"]

    task_subscribe_state = asyncio.create_task(subscribe_state(client))

    data = await gql_request(client, QUERY_STATE)
    assert "initialized" == data["state"]

    await asyncio.sleep(0.01)

    task_control_execution = asyncio.create_task(control_execution(client))

    await asyncio.sleep(0.01)

    data = await gql_request(client, MUTATE_EXEC)
    assert data["exec"]

    states, *_ = await asyncio.gather(
        task_subscribe_state,
        task_control_execution,
    )
    assert ["initialized", "running", "finished"] == states

    data = await gql_request(client, QUERY_STATE)
    assert "finished" == data["state"]

    await asyncio.sleep(0.01)


async def subscribe_state(client: TestClient) -> List[str]:
    ret = []
    async for data in gql_subscribe(client, SUBSCRIBE_STATE):
        s = data["state"]
        ret.append(s)
        if s == "finished":
            break
    return ret


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
        _, pending = await agen.asend(tasks)

    await asyncio.gather(*pending)


async def control_trace(client: TestClient, trace_id: int) -> None:
    # print(f'control_trace({trace_id})')

    async for data in gql_subscribe(
        client,
        SUBSCRIBE_PROMPTING,
        variables={"traceId": trace_id},
    ):
        state = data["prompting"]
        # print(state)
        if state["prompting"]:
            await asyncio.sleep(0.001)
            command = "continue"
            variables = {"traceId": trace_id, "command": command}
            data = await gql_request(
                client,
                MUTATE_SEND_PDB_COMMAND,
                variables=variables,
            )
            assert data["sendPdbCommand"]
