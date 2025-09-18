import asyncio
from collections.abc import AsyncIterator

import pytest

from nextlinegraphql.factory import create_app_for_test
from nextlinegraphql.plugins.graphql.test import TestClient


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    app = create_app_for_test()
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y
