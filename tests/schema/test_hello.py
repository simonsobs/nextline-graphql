from ariadne import graphql

import pytest
from unittest.mock import Mock

from nextlinegraphql import schema

##__________________________________________________________________||
@pytest.mark.asyncio
async def test_hello(snapshot):

    query = '''
      { hello }
    '''
    data = { 'query': query }

    request = Mock()
    request.headers = {'user-agent': 'Mozilla/5.0'}
    context_value = { 'request': request }
    success, response = await graphql(schema, data, context_value=context_value)
    assert success
    assert 'errors' not in response
    snapshot.assert_match(response)


##__________________________________________________________________||
