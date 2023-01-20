import pytest

from nextlinegraphql.plugins.db.pagination import SortField, load_models

from .models import Entity

params = [
    pytest.param(
        dict(sort=[SortField("num")]),
        [7, 8, 9, 10, 4, 5, 6, 1, 2, 3],
    ),
    pytest.param(
        dict(sort=[SortField("num", True)]),
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ),
    pytest.param(
        dict(sort=[SortField("txt")]),
        [1, 3, 4, 6, 7, 9, 2, 5, 8, 10],
    ),
    pytest.param(
        dict(sort=[SortField("txt", True)]),
        [2, 5, 8, 10, 1, 3, 4, 6, 7, 9],
    ),
    pytest.param(
        dict(sort=[SortField("num"), SortField("txt")]),
        [7, 9, 8, 10, 4, 6, 5, 1, 3, 2],
    ),
    pytest.param(
        dict(sort=[SortField("num")], after=5),
        [6, 1, 2, 3],
    ),
    pytest.param(
        dict(sort=[SortField("num")], after=5, first=3),
        [6, 1, 2],
    ),
    pytest.param(
        dict(sort=[SortField("num")], first=3),
        [7, 8, 9],
    ),
    pytest.param(
        dict(sort=[SortField("num", True)], after=5),
        [6, 7, 8, 9, 10],
    ),
    pytest.param(
        dict(sort=[SortField("num")], before=5),
        [7, 8, 9, 10, 4],
    ),
    pytest.param(
        dict(sort=[SortField("num")], before=5, last=3),
        [9, 10, 4],
    ),
    pytest.param(
        dict(sort=[SortField("num")], last=3),
        [1, 2, 3],
    ),
    pytest.param(
        dict(after=5),
        [6, 7, 8, 9, 10],
    ),
    pytest.param(
        dict(sort=[SortField("num"), SortField("txt")], after=5),
        [1, 3, 2],
    ),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_sort(session, kwargs, expected):
    Model = Entity
    id_field = "id"
    models = load_models(session, Model, id_field, **kwargs)
    assert expected == [m.id for m in models]
