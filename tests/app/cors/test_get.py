from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pytest import MonkeyPatch

from nextline_test_utils.strategies import st_none_or
from nextlinegraphql import create_app
from nextlinegraphql.plugins.graphql.test import TestClient

from .strategies import st_allow_origins, st_header_origin


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

    ## None or an origin that may be allowed
    ## If None, the request header does not include 'Origin'
    header_origin = data.draw(st_none_or(st_header_origin(allow_origins)))

    # Build the request header
    headers = {'accept': 'text/html'}
    if header_origin is not None:
        headers['origin'] = header_origin

    with monkeypatch.context() as m:
        # Configure with environment variables
        if allow_origins is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_ORIGINS', repr(allow_origins))

        app = create_app(
            enable_external_plugins=False,
            enable_logging_configuration=False,
            print_settings=False,
        )
        async with TestClient(app) as client:
            #
            resp = await client.get('/', headers=headers)

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
