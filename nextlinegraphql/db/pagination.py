from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.selectable import Select
from typing import Optional, List, NamedTuple, TypeVar

from . import models as db_models

import sqlparse


def format_sql(sql):
    return sqlparse.format(str(sql), reindent=True, keyword_case="upper")


class SortField(NamedTuple):
    field: str
    desc: bool = False


Sort = List[SortField]

_Id = TypeVar("_Id")


def load_models(
    session,
    Model: db_models.ModelType,
    id_field: str,
    *,
    sort: Optional[Sort] = None,
    before: Optional[_Id] = None,
    after: Optional[_Id] = None,
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
    before: Optional[_Id] = None,
    after: Optional[_Id] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Select:
    """Return a SELECT statement object to be given to session.scalars"""

    forward = (after is not None) or (first is not None)
    backward = (before is not None) or (last is not None)

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

    if not (forward or backward):
        return select(Model).order_by(*sorting_fields(Model))

    cursor = None
    if after is not None:
        cursor = after
    elif before is not None:
        cursor = before

    if cursor is not None:
        cte = select(
            Model,
            func.row_number()
            .over(order_by=sorting_fields(Model))
            .label("row_number"),
        ).cte()

        subq = select(cte.c.row_number.label("cursor"))
        subq = subq.where(getattr(cte.c, id_field) == cursor)
        subq = subq.subquery()

        Alias = aliased(Model, cte)
        stmt = select(Alias).select_from(cte)
        stmt = stmt.join(subq, True)  # cartesian product
        stmt = stmt.order_by(*sorting_fields(Alias))  # unnecessary?
        if after is not None:
            stmt = stmt.where(cte.c.row_number > subq.c.cursor)
        else:  # before
            stmt = stmt.where(cte.c.row_number < subq.c.cursor)
    else:
        stmt = select(Model).order_by(*sorting_fields(Model))

    if first is not None:
        stmt = stmt.limit(first)
    elif last is not None:
        Alias = aliased(Model, stmt.subquery())
        stmt = select(Alias).order_by(*sorting_fields(Alias, reverse=True))
        stmt = stmt.limit(last)

        Alias = aliased(Model, stmt.subquery())
        stmt = select(Alias).order_by(*sorting_fields(Alias))

    return stmt
