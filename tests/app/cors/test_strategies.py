import re
from urllib.parse import urlparse

from hypothesis import given

from .strategies import ALL_METHODS, st_headers, st_methods, st_origins


@given(origin=st_origins())
def test_origin(origin: str) -> None:
    parsed = urlparse(origin)
    assert f'{parsed.scheme}://{parsed.netloc}' == origin


@given(header=st_headers())
def test_header(header: str) -> None:
    pattern = r'^[A-Z][a-z]*(?:-[A-Z][a-z]*)*$'
    assert re.match(pattern, header)


@given(method=st_methods())
def test_method(method: str) -> None:
    assert method in ALL_METHODS
