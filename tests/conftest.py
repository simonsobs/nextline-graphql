import asyncio
from collections.abc import AsyncIterator

import pytest
from starlette.applications import Starlette

from nextlinegraphql import create_app
from nextlinegraphql.plugins.graphql.test import TestClient


@pytest.fixture
async def client(app: Starlette) -> AsyncIterator[TestClient]:
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


@pytest.fixture
def app(request: pytest.FixtureRequest) -> Starlette:
    # TODO: Use `enable_external_plugins=False` for the tests that
    #       don't need external plugins.
    return create_app()
