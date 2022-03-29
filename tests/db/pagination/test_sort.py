from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.future import select

import pytest


from nextlinegraphql.db.pagination import load_models

from .models import Entity


def test_sort(session):
    after = 5
    Model = Entity
    id_field = "id"
    order_by = [("num", False)]

    if id_field not in [f for f, _ in order_by]:
        order_by.append((id_field, False))

    def order_by_arg(Model):
        return [
            getattr(Model, f).desc() if d else getattr(Model, f)
            for f, d in order_by
        ]

    # sort and add row number
    stmt = select(
        Model,
        func.row_number()
        .over(order_by=order_by_arg(Model))
        .label("row_number"),
    )

    # find the row number of "after"
    subq = stmt.subquery()
    Alias = aliased(Model, subq)

    stmt = select(subq.c.row_number)
    stmt = stmt.where(Alias.id == after)

    # add the row number of "after" to all rows
    subq = stmt.subquery()
    stmt = select(
        Model,
        func.row_number()
        .over(order_by=order_by_arg(Model))
        .label("row_number"),
        subq.c.row_number.label("mark"),
    )
    stmt = stmt.join(subq, True)  # cross join

    # select rows with row numbers greater than that of "after"
    subq = stmt.subquery()
    Alias = aliased(Model, subq)
    stmt = select(Alias, subq.c.row_number, subq.c.mark)
    stmt = stmt.order_by(*order_by_arg(Alias))  # might be unnecessary
    stmt = stmt.where(subq.c.row_number > subq.c.mark)

    # models = session.execute(stmt)
    models = session.scalars(stmt)

    # models = models.all()
    # print(models)

    expected = [6, 1, 2, 3]
    assert expected == [m.id for m in models]
