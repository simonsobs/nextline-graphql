from string import ascii_lowercase

from hypothesis import provisional
from hypothesis import strategies as st

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
