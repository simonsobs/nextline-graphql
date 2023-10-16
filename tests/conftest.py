import asyncio
from typing import AsyncIterator

import pytest
from async_asgi_testclient import TestClient
from starlette.applications import Starlette

from nextlinegraphql import create_app


@pytest.fixture
async def client(app: Starlette) -> AsyncIterator[TestClient]:
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


@pytest.fixture
def app() -> Starlette:
    return create_app()
