import strawberry
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pytest import MonkeyPatch

from nextline_test_utils.strategies import st_none_or
from nextlinegraphql.factory import create_app_for_test
from nextlinegraphql.hook import spec
from nextlinegraphql.plugins.graphql.test import TestClient
from nextlinegraphql.plugins.graphql.test.funcs import PostRequest
from tests.app.cors.strategies import st_allow_origins, st_header_origin, st_origins


@strawberry.type
class QueryMock:
    @strawberry.field
    def foo(self) -> str:
        return 'bar'


@strawberry.type
class Query:
    @strawberry.field
    def mock(self) -> QueryMock:
        return QueryMock()


@strawberry.type
class MutationMock:
    @strawberry.mutation
    def baz(self) -> str:
        return 'qux'


@strawberry.type
class Mutation:
    @strawberry.field
    def mock(self) -> MutationMock:
        return MutationMock()


QUERY_FOO = '''
query {
  mock {
    foo
  }
}
'''

MUTATE_BAZ = '''
mutation {
  mock {
    baz
  }
}
'''


class MockPlugin:
    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, Mutation, None)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=st.data())
async def test_property(data: st.DataObject, monkeypatch: MonkeyPatch) -> None:
    '''Test CORS configurations.

    Useful links about CORS
    https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#simple_requests
    https://gist.github.com/FND/204ba41bf6ae485965ef

    '''
    # Draw from the strategies

    ## None, ['*'], or a list of origins
    ## If None, no environment variable is set, default to ['*']
    allow_origins = data.draw(st_none_or(st_allow_origins()))

    ## None, ['*'], or a list of origins
    ## If None, no environment variable is set, default to ['*']
    mutation_allow_origins = data.draw(
        st_none_or(
            st_allow_origins()
            if not allow_origins or '*' in allow_origins
            else st.lists(st.one_of(st.sampled_from(allow_origins), st_origins()))
        )
    )

    ## None or an origin that may be allowed
    ## If None, the request header does not include 'Origin'
    header_origin = data.draw(
        st_none_or(
            st_header_origin([*(allow_origins or []), *(mutation_allow_origins or [])])
        )
    )

    # Build the request header
    headers = {'Content-Type:': 'application/json'}
    if header_origin is not None:
        headers['origin'] = header_origin

    with monkeypatch.context() as m:
        # Configure with environment variables
        if allow_origins is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_ORIGINS', repr(allow_origins))

        if mutation_allow_origins is not None:
            m.setenv(
                'NEXTLINE_GRAPHQL__MUTATION_ALLOW_ORIGINS', repr(mutation_allow_origins)
            )

        mock_plugin = MockPlugin()
        app = create_app_for_test(extra_plugins=[mock_plugin])
        async with TestClient(app) as client:
            QUERY = data.draw(st.sampled_from([QUERY_FOO, MUTATE_BAZ]))
            request = PostRequest(query=QUERY)
            resp = await client.post('/', json=request, headers=headers)

            # Successfully processed regardless of whether the origin is allowed
            assert resp.status_code == 200

            # Assert 'Access-Control-Allow-Origin'
            if header_origin is None:
                'access-control-allow-origin' not in resp.headers
            elif allow_origins == ['*'] or allow_origins is None:
                assert '*' == resp.headers['access-control-allow-origin']
            elif header_origin in allow_origins:
                assert header_origin == resp.headers['access-control-allow-origin']
            else:
                'access-control-allow-origin' not in resp.headers

            # Assert the response content
            if QUERY == QUERY_FOO:
                assert resp.json() == {'data': {'mock': {'foo': 'bar'}}}
            elif QUERY == MUTATE_BAZ:
                if header_origin is None:
                    assert resp.json() == {'data': {'mock': {'baz': 'qux'}}}
                elif (
                    mutation_allow_origins == ['*']
                    or mutation_allow_origins is None
                    or header_origin in mutation_allow_origins
                ):
                    assert resp.json() == {'data': {'mock': {'baz': 'qux'}}}
                else:
                    assert resp.json() == {
                        'data': None,
                        'errors': [{'message': 'GraphQL Mutations not allowed'}],
                    }
