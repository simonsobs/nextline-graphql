from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.future import select

import sqlparse

import pytest


from nextlinegraphql.db.pagination import load_models

from .models import Entity

params = [
    pytest.param(
        dict(sort=[("num", False)], after=5),
        [6, 1, 2, 3],
    ),
    pytest.param(
        dict(sort=[("num", True)], after=5),
        [6, 7, 8, 9, 10],
    ),
    pytest.param(
        dict(after=5),
        [6, 7, 8, 9, 10],
    ),
    pytest.param(
        dict(sort=[("num", False), ("txt", False)], after=5),
        [1, 3, 2],
    ),
]


@pytest.mark.parametrize("kwargs, expected", params)
def test_sort(session, kwargs, expected):
    after = kwargs.get("after")
    sort = kwargs.get("sort", [])
    Model = Entity
    id_field = "id"

    if id_field not in [f for f, _ in sort]:
        sort.append((id_field, False))

    def order_by_arg(Model):
        return [
            getattr(Model, f).desc() if d else getattr(Model, f)
            for f, d in sort
        ]

    # sort and add row number
    cte = select(
        Model,
        func.row_number()
        .over(order_by=order_by_arg(Model))
        .label("row_number"),
    )
    cte = cte.cte()

    # find the row number of "after"
    subq = select(cte.c.row_number.label("cursor"))
    subq = subq.where(getattr(cte.c, id_field) == after)
    subq = subq.subquery()

    Alias = aliased(Model, cte)
    stmt = select(Alias).select_from(cte)
    stmt = stmt.join(subq, True)  # cartesian product
    stmt = stmt.order_by(*order_by_arg(Alias))  # might be unnecessary
    stmt = stmt.where(cte.c.row_number > subq.c.cursor)

    print()
    print("-" * 100)
    print(format_sql(str(stmt)))
    models = session.execute(stmt)
    models = models.all()
    print(models)
    # return

    # models = session.execute(stmt)
    models = session.scalars(stmt)

    models = models.all()
    print(models)

    assert expected == [m.id for m in models]


def format_sql(sql):
    return sqlparse.format(str(sql), reindent=True, keyword_case="upper")
