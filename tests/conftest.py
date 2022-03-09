import asyncio
import sys
import threading

import pytest
from async_asgi_testclient import TestClient

from nextlinegraphql import create_app


@pytest.fixture(autouse=True)
def recover_trace():
    """Set the original trace function back after each test"""
    trace_org = sys.gettrace()
    yield
    sys.settrace(trace_org)
    threading.settrace(trace_org)


@pytest.fixture
async def client():
    async with TestClient(create_app()) as y:
        await asyncio.sleep(0)
        yield y
