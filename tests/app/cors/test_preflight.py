from hypothesis import HealthCheck, given, note, settings
from hypothesis import strategies as st
from pytest import MonkeyPatch

from nextline_test_utils.strategies import st_none_or
from nextlinegraphql.factory import create_app_for_test
from nextlinegraphql.plugins.graphql.test import TestClient

from .strategies import (
    ALLOWED_METHODS,
    ALWAYS_ALLOWED_HEADERS,
    st_allow_origins,
    st_header_origin,
    st_headers,
    st_methods,
)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(data=st.data())
async def test_property(data: st.DataObject, monkeypatch: MonkeyPatch) -> None:
    '''Test CORS configurations for preflighted requests.

    https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#preflighted_requests
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS#preflighted_requests_in_cors

    TODO: This test is slow. Disable all external plugins to speed it up.
    '''
    # Draw from the strategies

    ## allow_origins: an env var NEXTLINE_CORS__ALLOW_ORIGINS
    ## None, ['*'], or a list of origins
    ## If None, the environment variable is not set, default to ['*']
    allow_origins = data.draw(st_none_or(st_allow_origins()), label='allow_origins')

    ## allow_headers: an env var NEXTLINE_CORS__ALLOW_HEADERS
    ## None, ['*'], or a list of headers
    ## If None, the environment variable is not set, default to ['*']
    allow_headers = data.draw(
        st.one_of(st.none(), st.just(['*']), st.lists(st_headers())),
        label='allow_headers',
    )

    ## allow_credentials: an env var NEXTLINE_CORS__ALLOW_CREDENTIALS
    ## None or a boolean
    ## True only if neither `allow_origins` nor `allow_headers` is None or ['*']
    ## If None, the environment variable is not set, default to False
    if allow_origins not in (None, ['*']) and allow_headers not in (None, ['*']):
        st_allow_credentials = st_none_or(st.booleans())
    else:
        st_allow_credentials = st_none_or(st.just(False))
    allow_credentials = data.draw(st_allow_credentials, label='allow_credentials')

    ## header_origin: an HTTP request header 'Origin'
    header_origin = data.draw(st_header_origin(allow_origins), label='header_origin')

    ## header_request_method: an HTTP request header 'Access-Control-Request-Method'
    header_request_method = data.draw(st_methods(), label='header_request_method')

    # All allowed headers except for the wildcard '*'
    allowed_headers = set(ALWAYS_ALLOWED_HEADERS) | (set(allow_headers or []) - {'*'})

    ## header_request_headers: an HTTP request header 'Access-Control-Request-Headers'
    ## None or a list of headers
    ## If None, the request header does not include 'Access-Control-Request-Headers'
    header_request_headers = data.draw(
        st_none_or(
            st.lists(
                st.one_of(st_headers(), st.sampled_from(list(allowed_headers))),
                unique=True,
            )
        ),
        label='header_request_headers',
    )

    # Build the request header
    headers = {
        'Origin': header_origin,
        'Access-Control-Request-Method': header_request_method,
    }
    if header_request_headers is not None:
        headers['Access-Control-Request-Headers'] = ', '.join(header_request_headers)

    with monkeypatch.context() as m:
        # Configure with environment variables
        if allow_origins is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_ORIGINS', repr(allow_origins))
        if allow_headers is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_HEADERS', repr(allow_headers))
        if allow_credentials is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_CREDENTIALS', str(allow_credentials).lower())

        app = create_app_for_test()
        async with TestClient(app) as client:
            #
            resp = await client.options('/', headers=headers)
            note(resp.headers)
            note(resp.text)

            # Assert the status code
            if is_response_error_expected(
                allow_origins,
                allow_headers,
                header_origin,
                header_request_method,
                header_request_headers,
            ):
                assert 400 <= resp.status_code < 410
                return

            assert resp.status_code == 200

            # Assert 'Access-Control-Allow-Origin'
            if allow_origins == ['*'] or allow_origins is None:
                assert '*' == resp.headers['access-control-allow-origin']
            else:
                assert header_origin == resp.headers['access-control-allow-origin']

            # Assert 'Access-Control-Allow-Methods'
            assert set(ALLOWED_METHODS) == set(
                m.strip()
                for m in resp.headers['access-control-allow-methods'].split(', ')
            )

            # Assert 'Access-Control-Allow-Headers'
            if header_request_headers is None:
                'access-control-allow-headers' not in resp.headers
            else:
                set(header_request_headers) == set(
                    m.strip()
                    for m in resp.headers['access-control-allow-headers'].split(', ')
                )


def is_response_error_expected(
    allow_origins: list[str] | None,
    allow_headers: list[str] | None,
    header_origin: str,
    header_request_method: str,
    header_request_headers: list[str] | None,
) -> bool:
    # Origin:
    if allow_origins is not None and allow_origins != ['*']:
        if header_origin not in allow_origins:
            return True

    # Request method:
    if header_request_method not in ALLOWED_METHODS:
        return True

    # Request headers:
    # Headers don't need to have 'Access-Control-Request-Headers'.
    # If it does, the headers must be allowed.
    if header_request_headers is None:
        return False

    if allow_headers is not None and allow_headers != ['*']:
        if header_request_headers == []:
            return True

        allowed_headers = set(ALWAYS_ALLOWED_HEADERS) | set(allow_headers)
        if set(header_request_headers) - allowed_headers:
            return True

    return False
