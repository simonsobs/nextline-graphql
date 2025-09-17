import re
from urllib.parse import urlparse

from hypothesis import given
from hypothesis import strategies as st

from .strategies import (
    ALL_METHODS,
    st_allow_origins,
    st_header_origin,
    st_headers,
    st_methods,
    st_origins,
)


@given(origin=st_origins())
def test_origin(origin: str) -> None:
    assert _is_valid_origin(origin)


@given(header=st_headers())
def test_header(header: str) -> None:
    pattern = r'^[A-Z][a-z]*(?:-[A-Z][a-z]*)*$'
    assert re.match(pattern, header)


@given(method=st_methods())
def test_method(method: str) -> None:
    assert method in ALL_METHODS


@given(allow_origins=st_allow_origins())
def test_allow_origins(allow_origins: list[str] | None) -> None:
    if allow_origins is None:
        return

    if '*' in allow_origins:
        return

    assert all(_is_valid_origin(o) for o in allow_origins)


@given(data=st.data())
def test_header_origin(data: st.DataObject) -> None:
    allow_origins = data.draw(st_allow_origins())
    header_origin = data.draw(st_header_origin(allow_origins))

    if header_origin is None:
        return

    if allow_origins and '*' not in allow_origins:
        if header_origin in allow_origins:
            return

    assert _is_valid_origin(header_origin)


def _is_valid_origin(origin: str) -> bool:
    parsed = urlparse(origin)
    return f'{parsed.scheme}://{parsed.netloc}' == origin
