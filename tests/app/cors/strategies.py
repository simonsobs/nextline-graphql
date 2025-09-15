from string import ascii_lowercase

from hypothesis import provisional
from hypothesis import strategies as st


def st_origins() -> st.SearchStrategy[str]:
    '''A strategy for origins.

    E.g.  `https://example.com:8080`
    '''

    # `schemes` and `ports` copied from `provisional.urls()`
    schemes = st.sampled_from(['http', 'https'])
    ports = st.integers(min_value=1, max_value=2**16 - 1).map(':{}'.format)

    return st.builds(
        '{}://{}{}'.format,
        schemes,
        provisional.domains(),
        st.just('') | ports,
    )


# https://www.starlette.io/middleware/#corsmiddleware
ALWAYS_ALLOWED_HEADERS = (
    'Accept',
    'Accept-Language',
    'Content-Language',
    'Content-Type',
)

# Methods allowed when `allow_methods` is set to `['*']`
ALL_METHODS = ('DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT')

# Specified in `factory.py`
ALLOWED_METHODS = ('GET', 'POST', 'OPTIONS')


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
