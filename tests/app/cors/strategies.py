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
