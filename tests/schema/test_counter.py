from ariadne import graphql, subscribe

import pytest
from unittest.mock import AsyncMock, Mock

from nextlinegraphql import schema

##__________________________________________________________________||
@pytest.fixture(autouse=True)
def mock_asyncio_sleep(monkeypatch):
    import asyncio
    y = Mock(wraps=asyncio)
    y.sleep = AsyncMock()
    monkeypatch.setattr("nextlinegraphql.bindables.asyncio", y)
    yield y

##__________________________________________________________________||
@pytest.mark.asyncio
async def test_counter(snapshot):

    query = '''
      subscription {
        counter
      }
    '''

    data = { 'query': query }
    success, result = await subscribe(schema, data)
    assert success
    response = await result.__anext__()
    snapshot.assert_match(response.data)
    response = await result.__anext__()
    snapshot.assert_match(response.data)
    response = await result.__anext__()
    snapshot.assert_match(response.data)
    response = await result.__anext__()
    snapshot.assert_match(response.data)
    response = await result.__anext__()
    snapshot.assert_match(response.data)
    with pytest.raises(StopAsyncIteration):
        response = await result.__anext__()

##__________________________________________________________________||
