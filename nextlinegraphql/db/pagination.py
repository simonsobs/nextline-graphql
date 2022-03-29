from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.selectable import Select
from typing import Optional, List, NamedTuple

from . import models as db_models


class SortField(NamedTuple):
    field: str
    desc: bool = False


Sort = List[SortField]


def load_models(
    session,
    Model: db_models.ModelType,
    id_field: str,
    *,
    sort: Optional[Sort] = None,
    before: Optional[int] = None,
    after: Optional[int] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
):
    stmt = compose_statement(
        Model,
        id_field,
        sort=sort,
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
    sort: Optional[Sort] = None,
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

    sort = sort or []

    if id_field not in [s.field for s in sort]:
        sort.append(SortField(id_field))

    def sorting_fields(Model, reverse=False):
        return [
            f.desc() if reverse ^ d else f
            for f, d in [(getattr(Model, s.field), s.desc) for s in sort]
        ]

    stmt = select(Model)

    if forward:
        if after:
            cte = select(
                Model,
                func.row_number()
                .over(order_by=sorting_fields(Model))
                .label("row_number"),
            ).cte()

            subq = select(cte.c.row_number.label("cursor"))
            subq = subq.where(getattr(cte.c, id_field) == after)
            subq = subq.subquery()

            Alias = aliased(Model, cte)
            stmt = select(Alias).select_from(cte)
            stmt = stmt.join(subq, True)  # cartesian product
            stmt = stmt.order_by(*sorting_fields(Alias))  # unnecessary?
            stmt = stmt.where(cte.c.row_number > subq.c.cursor)
        else:
            stmt = stmt.order_by(*sorting_fields(Model))
        if first is not None:
            stmt = stmt.limit(first)

    elif backward:
        if before:
            stmt = stmt.where(getattr(Model, id_field) < before)
        if last is None:
            stmt = stmt.order_by(*sorting_fields(Model))
        else:
            # use subquery to limit from last
            # https://stackoverflow.com/a/12125925/7309855
            # subq = stmt.order_by(getattr(Model, id_field).desc())
            subq = stmt.order_by(*sorting_fields(Model, reverse=True))
            subq = subq.limit(last)

            # alias to refer a subquery as an ORM
            # https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#orm-entity-subqueries-ctes
            Alias = aliased(Model, subq.subquery())

            stmt = select(Alias)
            stmt = stmt.order_by(*sorting_fields(Alias))

    else:
        stmt = stmt.order_by(*sorting_fields(Model))

    return stmt
