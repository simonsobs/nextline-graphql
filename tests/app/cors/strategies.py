from string import ascii_lowercase

from hypothesis import provisional
from hypothesis import strategies as st

from nextline_test_utils.strategies import st_none_or

# Headers always allowed by CORS.
# https://www.starlette.io/middleware/#corsmiddleware
ALWAYS_ALLOWED_HEADERS = (
    'Accept',
    'Accept-Language',
    'Content-Language',
    'Content-Type',
)

# HTTP methods allowed when `allow_methods` is set to `['*']`.
ALL_METHODS = ('DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT')

# HTTP methods hard-coded to be allowed in `factory.py`.
ALLOWED_METHODS = ('GET', 'POST', 'OPTIONS')


def st_origins() -> st.SearchStrategy[str]:
    '''A strategy for HTTP origins.

    The HTTP origin consists of scheme, host, and optional port.
    E.g., `https://example.com:8080`

    '''

    # `schemes` and `ports` copied from `provisional.urls()`
    st_schemes = st.sampled_from(['http', 'https'])
    st_ports = st.integers(min_value=1, max_value=2**16 - 1).map(':{}'.format)

    return st.builds(
        '{}://{}{}'.format,
        st_schemes,
        provisional.domains(),
        st.just('') | st_ports,
    )


def st_headers() -> st.SearchStrategy[str]:
    '''A strategy for HTTP headers.

    One of the always allowed headers or a random header.
    E.g., `Content-Type`, Nykbjacgeh-Kgvudhdbup-Nj`

    '''
    return st.one_of(
        st.sampled_from(ALWAYS_ALLOWED_HEADERS),
        st.builds(
            '-'.join,
            st.lists(
                st.text(ascii_lowercase, min_size=1, max_size=10).map(
                    lambda s: s.capitalize()
                ),
                min_size=1,
            ),
        ),
    )


def st_methods() -> st.SearchStrategy[str]:
    '''A strategy for HTTP methods.

    One of the methods either allowed or not allowed by the CORS.
    E.g., `DELETE`, `GET`, `HEAD`, `OPTIONS`, `PATCH`, `POST`, `PUT`

    '''
    return st.sampled_from(ALL_METHODS)


def st_allow_origins() -> st.SearchStrategy[list[str] | None]:
    '''A strategy for allowed CORS origins.

    None, ['*'], or a list of origins.
    '''
    return st.one_of(st.none(), st.just(['*']), st.lists(st_origins()))


def st_header_origin(allow_origins: list[str] | None) -> st.SearchStrategy[str | None]:
    '''A strategy for an HTTP request header 'Origin'.

    None or an origin that may be allowed.
    '''
    return st_none_or(
        st_origins()
        if not allow_origins or '*' in allow_origins
        else st.one_of(st.sampled_from(allow_origins), st_origins())
    )
