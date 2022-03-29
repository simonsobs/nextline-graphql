from sqlalchemy import func
from sqlalchemy.orm import aliased
from sqlalchemy.future import select

import pytest


from nextlinegraphql.db.pagination import load_models

from .models import Entity


def test_sort(session):
    after = 5
    Model = Entity
    stmt = select(Model)
    stmt = stmt.order_by(Model.num)
    stmt = stmt.order_by(Model.id)
    print()
    print(stmt)
    models = session.scalars(stmt)
    print(list(models))

    stmt = select(
        Model,
        func.row_number()
        .over(order_by=[Model.num, Model.id])
        .label("row_number"),
    )
    # stmt = stmt.order_by(Model.num)
    # stmt = stmt.order_by(Model.id)
    # stmt = stmt.where(Model.id <= 2)
    print()
    print(stmt)
    models = session.execute(stmt)
    print(models.all())
    print("-" * 100)

    subq = stmt.subquery()
    Alias = aliased(Model, subq)

    # stmt = select(Alias, subq.c.row_number)
    stmt = select(subq.c.row_number)
    stmt = stmt.order_by(subq.c.row_number)
    stmt = stmt.where(Alias.id == after)
    print(stmt)
    models = session.execute(stmt)
    print(models.all())
    print("-" * 100)

    subq = stmt.subquery()

    stmt = select(
        Model,
        func.row_number()
        .over(order_by=[Model.num, Model.id])
        .label("row_number"),
        subq.c.row_number.label("mark"),
    )
    # stmt = select(Model, subq.c.row_number)
    stmt = stmt.join(subq, True)
    # stmt = stmt.where(text("row_number > mark"))
    # print(stmt)
    # models = session.execute(stmt)
    # print(models.all())

    # stmt = select(Model)
    # stmt = stmt.join(subq, Model.id == subq.c.id)
    # stmt = stmt.order_by(subq.c.row_number)
    # print(stmt)
    # models = session.execute(stmt)
    # print(models.all())

    subq = stmt.subquery()
    Alias = aliased(Model, subq)
    stmt = select(Alias, subq.c.row_number, subq.c.mark)
    stmt = stmt.order_by(Alias.num)
    stmt = stmt.order_by(Alias.id)
    stmt = stmt.where(subq.c.row_number > subq.c.mark)
    print(stmt)
    # models = session.execute(stmt)
    models = session.scalars(stmt)

    # models = models.all()
    # print(models)

    expected = [6, 1, 2, 3]
    assert expected == [m.id for m in models]
