import sys
from ariadne import graphql, subscribe

import pytest
from unittest.mock import AsyncMock, Mock

from nextlinegraphql.schema import schema


##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_asyncio_sleep(monkeypatch):
    import asyncio

    y = Mock(wraps=asyncio)
    y.sleep = AsyncMock()
    module = sys.modules["nextlinegraphql.schema.bindables"]
    monkeypatch.setattr(module, "asyncio", y)
    yield y


##__________________________________________________________________||
@pytest.mark.asyncio
async def test_query():

    query = """
      { hello }
    """
    data = {"query": query}

    request = Mock()
    request.headers = {"user-agent": "Mozilla/5.0"}
    context_value = {"request": request}
    success, response = await graphql(
        schema, data, context_value=context_value
    )
    assert success
    assert "errors" not in response
    expect = {"data": {"hello": "Hello, Mozilla/5.0!"}}
    assert expect == response


##__________________________________________________________________||
@pytest.mark.asyncio
async def test_subscription():

    query = """
      subscription {
        counter
      }
    """

    data = {"query": query}
    success, result = await subscribe(schema, data)
    assert success

    response = await result.__anext__()
    expect = {"counter": 1}
    assert expect == response.data

    response = await result.__anext__()
    expect = {"counter": 2}
    assert expect == response.data

    response = await result.__anext__()
    expect = {"counter": 3}
    assert expect == response.data

    response = await result.__anext__()
    expect = {"counter": 4}
    assert expect == response.data

    response = await result.__anext__()
    expect = {"counter": 5}
    assert expect == response.data

    with pytest.raises(StopAsyncIteration):
        response = await result.__anext__()


##__________________________________________________________________||
