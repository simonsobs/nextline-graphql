import asyncio
from collections.abc import AsyncIterator

import pytest

from nextlinegraphql import create_app
from nextlinegraphql.plugins.graphql.test import TestClient


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    app = create_app(enable_external_plugins=False, enable_logging_configuration=False)
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y
