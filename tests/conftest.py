import asyncio
import sys
import threading

import pytest
from async_asgi_testclient import TestClient

from nextlinegraphql import create_app
from nextlinegraphql.db import DB


@pytest.fixture(autouse=True)
def recover_trace():
    """Set the original trace function back after each test"""
    trace_org = sys.gettrace()
    yield
    sys.settrace(trace_org)
    threading.settrace(trace_org)


@pytest.fixture
async def client(app):
    async with TestClient(app) as y:
        await asyncio.sleep(0)
        yield y


@pytest.fixture
def app(config, db: DB, nextline):
    return create_app(
        config=config,
        db=db,
        nextline=nextline,
    )


@pytest.fixture
def config():
    return None


@pytest.fixture
def db():
    return None


@pytest.fixture
def nextline():
    return None
