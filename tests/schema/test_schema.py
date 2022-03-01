from ariadne import graphql

import pytest

from nextlinegraphql import schema


@pytest.mark.xfail()
@pytest.mark.asyncio
async def test_schema(snapshot):

    query = """
      {
        __schema {
          types {
            name
            description
            fields {
              name
              description
              type {
                name
              }
            }
            inputFields {
              name
              description
              defaultValue
            }
          }
        }
      }
    """

    data = {"query": query}
    success, response = await graphql(schema, data)
    assert success
    assert "errors" not in response
    snapshot.assert_match(response)
