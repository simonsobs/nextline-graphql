from string import ascii_lowercase

from hypothesis import HealthCheck, Phase, given, note, settings
from hypothesis import strategies as st
from pytest import MonkeyPatch

from nextline_test_utils.strategies import st_none_or
from nextlinegraphql import create_app
from nextlinegraphql.plugins.graphql.test import TestClient

from .strategies import (
    ALLOWED_METHODS,
    ALWAYS_ALLOWED_HEADERS,
    st_headers,
    st_methods,
    st_origins,
)


@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    phases=[Phase.generate],
)
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
    allow_origins = data.draw(
        st.one_of(st.none(), st.just(['*']), st.lists(st_origins())),
        label='allow_origins',
    )

    ## allow_headers: an env var NEXTLINE_CORS__ALLOW_HEADERS
    ## None, ['*'], or a list of headers
    ## If None, the environment variable is not set, default to ['*']
    allow_headers = data.draw(
        st.one_of(st.none(), st.just(['*']), st.lists(st_headers())),
        label='allow_headers',
    )

    ## header_origin: an HTTP request header 'Origin'
    ## None or an origin
    ## If None, the request header does not include 'Origin'
    header_origin = data.draw(
        st_none_or(
            st_origins()
            if not allow_origins or '*' in allow_origins
            else st.one_of(st_origins(), st.sampled_from(allow_origins))
        ),
        label='header_origin',
    )

    ## header_request_method: an HTTP request header 'Access-Control-Request-Method'
    ## None or a method
    ## If None, the request header does not include 'Access-Control-Request-Method'
    header_request_method = data.draw(
        st_none_or(st_methods()), label='header_request_method'
    )

    # All allowed headers except for the wildcard '*'
    allowed_headers = set(ALWAYS_ALLOWED_HEADERS) | (set(allow_headers or []) - {'*'})

    ## header_request_headers: an HTTP request header 'Access-Control-Request-Headers'
    ## None or a list of headers
    ## If None, the request header does not include 'Access-Control-Request-Headers'
    header_request_headers = data.draw(
        st_none_or(
            st.lists(st.one_of(st_headers(), st.sampled_from(list(allowed_headers))))
        ),
        label='header_request_headers',
    )

    # Build the request header
    headers: dict[str, str] = {}
    if header_origin is not None:
        headers['Origin'] = header_origin
    if header_request_method is not None:
        headers['Access-Control-Request-Method'] = header_request_method
    if header_request_headers is not None:
        headers['Access-Control-Request-Headers'] = ', '.join(header_request_headers)

    with monkeypatch.context() as m:
        # Configure with environment variables
        if allow_origins is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_ORIGINS', repr(allow_origins))
        if allow_headers is not None:
            m.setenv('NEXTLINE_CORS__ALLOW_HEADERS', repr(allow_headers))

        app = create_app()
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
            if header_origin is None:
                'access-control-allow-origin' not in resp.headers
            elif allow_origins == ['*'] or allow_origins is None:
                assert '*' == resp.headers['access-control-allow-origin']
            elif header_origin in allow_origins:
                assert header_origin == resp.headers['access-control-allow-origin']
            else:
                'access-control-allow-origin' not in resp.headers

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
    header_origin: str | None,
    header_request_method: str | None,
    header_request_headers: list[str] | None,
) -> bool:
    # Origin:
    # Headers must have 'Origin' with a value that is allowed.
    if header_origin is None:
        return True

    if allow_origins is not None and allow_origins != ['*']:
        if header_origin not in allow_origins:
            return True

    # Request method:
    # Headers must have 'Access-Control-Request-Method' with a value that is allowed.
    if header_request_method is None:
        return True

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
