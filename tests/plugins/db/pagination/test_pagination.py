import pytest

from nextlinegraphql.plugins.db.pagination import load_models

from .models import Entity


def test_all(session):
    Model = Entity
    models = load_models(session, Model, "id")
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert expected == [m.id for m in models]


params = [
    pytest.param(dict(first=0), [], id="zero"),
    pytest.param(dict(first=1), [1], id="one"),
    pytest.param(dict(first=3), [1, 2, 3], id="some"),
    pytest.param(dict(first=9), [1, 2, 3, 4, 5, 6, 7, 8, 9], id="one-fewer"),
    pytest.param(dict(first=10), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], id="exact"),
    pytest.param(dict(first=11), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], id="one-more"),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_forward(session, kwargs, expected):
    Model = Entity
    models = load_models(session, Model, "id", **kwargs)
    assert expected == [m.id for m in models]


params = [
    pytest.param(dict(after=1), [2, 3, 4, 5, 6, 7, 8, 9, 10], id="one"),
    pytest.param(dict(after=5), [6, 7, 8, 9, 10], id="middle"),
    pytest.param(dict(after=9), [10], id="one-before-last"),
    pytest.param(dict(after=10), [], id="last"),
    pytest.param(dict(after=7, first=1), [8], id="first-one"),
    pytest.param(dict(after=7, first=2), [8, 9], id="first-one-fewer"),
    pytest.param(dict(after=7, first=3), [8, 9, 10], id="first-exact"),
    pytest.param(dict(after=7, first=4), [8, 9, 10], id="first-one-more"),
    pytest.param(dict(after=10, first=1), [], id="first-one-after-last"),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_forward_with_after(session, kwargs, expected):
    Model = Entity
    models = load_models(session, Model, "id", **kwargs)
    assert expected == [m.id for m in models]


params = [
    pytest.param(dict(last=0), [], id="zero"),
    pytest.param(dict(last=1), [10], id="one"),
    pytest.param(dict(last=3), [8, 9, 10], id="some"),
    pytest.param(dict(last=9), [2, 3, 4, 5, 6, 7, 8, 9, 10], id="one-fewer"),
    pytest.param(dict(last=10), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], id="exact"),
    pytest.param(dict(last=11), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], id="one-more"),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_backward(session, kwargs, expected):
    Model = Entity
    models = load_models(session, Model, "id", **kwargs)
    assert expected == [m.id for m in models]


params = [
    pytest.param(dict(before=10), [1, 2, 3, 4, 5, 6, 7, 8, 9], id="one"),
    pytest.param(dict(before=5), [1, 2, 3, 4], id="middle"),
    pytest.param(dict(before=2), [1], id="one-before-first"),
    pytest.param(dict(before=1), [], id="first"),
    pytest.param(dict(before=4, last=1), [3], id="last-one"),
    pytest.param(dict(before=4, last=2), [2, 3], id="last-one-fewer"),
    pytest.param(dict(before=4, last=3), [1, 2, 3], id="last-exact"),
    pytest.param(dict(before=4, last=4), [1, 2, 3], id="last-one-more"),
    pytest.param(dict(before=1, last=1), [], id="last-one-before-last"),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_backward_with_before(session, kwargs, expected):
    Model = Entity
    models = load_models(session, Model, "id", **kwargs)
    assert expected == [m.id for m in models]
