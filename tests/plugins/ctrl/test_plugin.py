import asyncio
from collections.abc import AsyncIterator

import pytest

from nextlinegraphql.factory import create_app_for_test
from nextlinegraphql.plugins.ctrl.graphql import (
    MUTATE_RUN_AND_CONTINUE,
    QUERY_STATE,
    SUBSCRIBE_STATE,
)
from nextlinegraphql.plugins.graphql.test import TestClient, gql_request, gql_subscribe


async def test_plugin(client: TestClient) -> None:
    data = await gql_request(client, QUERY_STATE)
    assert data['ctrl']['state'] == 'initialized'

    task = asyncio.create_task(_subscribe_state(client))

    data = await gql_request(client, MUTATE_RUN_AND_CONTINUE)
    assert data['ctrl']['runAndContinue']

    states = await task
    assert states == ['initialized', 'running', 'finished']


async def _subscribe_state(client: TestClient) -> list[str]:
    ret = []
    async for data in gql_subscribe(client, SUBSCRIBE_STATE):  # pragma: no branch
        s = data['ctrlState']
        ret.append(s)
        if s == 'finished':
            break
    return ret


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    app = create_app_for_test()
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y
