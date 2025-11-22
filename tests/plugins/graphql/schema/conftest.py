import pytest
from strawberry import Schema

from nextline_graphql.plugins.graphql.schema import Query


@pytest.fixture(scope='session')
def schema() -> Schema:
    '''GraphQL schema

    The scope is `session` because Hypothesis doesn't allow function-scoped
    fixtures. This is fine as the schema is stateless.
    '''
    return Schema(query=Query)
