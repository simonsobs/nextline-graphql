import pytest
from nextlinegraphql.db.pagination import load_models, SortField
from .models import Entity


params = [
    pytest.param(
        dict(sort=[SortField("num")]),
        [6, 7, 8, 9, 3, 4, 5, 0, 1, 2],
    ),
    pytest.param(
        dict(sort=[SortField("num")], after=0),
        [1, 2],
    ),
    pytest.param(
        dict(sort=[SortField("num")], before=0),
        [6, 7, 8, 9, 3, 4, 5],
    ),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_one(session, kwargs, expected):
    Model = Entity
    id_field = "id"
    models = load_models(session, Model, id_field, **kwargs)
    assert expected == [m.id for m in models]


params = [
    pytest.param(
        dict(sort=[SortField("num")]),
        ["F", "G", "H", "I", "C", "D", "E", "", "A", "B"],
    ),
    pytest.param(
        dict(sort=[SortField("num")], after=""),
        ["A", "B"],
    ),
    pytest.param(
        dict(sort=[SortField("num")], before=""),
        ["F", "G", "H", "I", "C", "D", "E"],
    ),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_str(session, kwargs, expected):
    Model = Entity
    id_field = "txt"
    models = load_models(session, Model, id_field, **kwargs)
    assert expected == [getattr(m, id_field) for m in models]


@pytest.fixture
def sample(db):
    with db.begin() as session:
        num = [3, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        txt = ["", "A", "B", "C", "D", "E", "F", "G", "H", "I"]
        for i in range(10):
            model = Entity(id=i, num=num[i], txt=txt[i])
            session.add(model)
