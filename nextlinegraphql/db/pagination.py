from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.selectable import Select
from typing import Optional

from . import models as db_models


def load_models(
    session,
    Model: db_models.ModelType,
    id_field: str,
    *,
    before: Optional[int] = None,
    after: Optional[int] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
):
    stmt = compose_statement(
        Model,
        id_field,
        before=before,
        after=after,
        first=first,
        last=last,
    )

    models = session.scalars(stmt)
    return models


def compose_statement(
    Model: db_models.ModelType,
    id_field: str,
    *,
    before: Optional[int] = None,
    after: Optional[int] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Select:
    """Return a SELECT statement object to be given to session.scalars"""

    forward = after or (first is not None)
    backward = before or (last is not None)

    if forward and backward:
        raise ValueError("Only either after/first or before/last is allowed")

    stmt = select(Model)

    if forward:
        if after:
            stmt = stmt.where(getattr(Model, id_field) > after)
        stmt = stmt.order_by(getattr(Model, id_field))
        if first is not None:
            stmt = stmt.limit(first)

    elif backward:
        if before:
            stmt = stmt.where(getattr(Model, id_field) < before)
        if last is None:
            stmt = stmt.order_by(getattr(Model, id_field))
        else:
            # use subquery to limit from last
            # https://stackoverflow.com/a/12125925/7309855
            subq = stmt.order_by(getattr(Model, id_field).desc())
            subq = subq.limit(last)

            # alias to refer a subquery as an ORM
            # https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#orm-entity-subqueries-ctes
            Alias = aliased(Model, subq.subquery())

            stmt = select(Alias).order_by(getattr(Alias, id_field))

    else:
        stmt = stmt.order_by(getattr(Model, id_field))

    return stmt
