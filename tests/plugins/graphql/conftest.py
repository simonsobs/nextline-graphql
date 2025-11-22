import asyncio
from collections.abc import AsyncIterator

import pytest

from nextline_graphql.factory import create_app_for_test
from nextline_graphql.plugins.graphql.test import TestClient


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    app = create_app_for_test()
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y
