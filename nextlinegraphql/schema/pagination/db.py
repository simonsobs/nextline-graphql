from __future__ import annotations
from functools import partial
import base64
from strawberry.types import Info
from sqlalchemy.future import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql.selectable import Select
from typing import Callable, List, TypeVar, Optional

from ...db import models as db_models
from .connection import query_connection, Connection, Edge


def encode_id(id: int) -> str:
    return base64.b64encode(f"{id}".encode()).decode()


def decode_id(cursor: str) -> int:
    return int(base64.b64decode(cursor).decode())


_T = TypeVar("_T")


def load_connection(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model: Callable[..., _T],
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> Connection[_T]:

    query_edges = partial(
        load_edges,
        Model=Model,
        id_field=id_field,
        create_node_from_model=create_node_from_model,
    )

    return query_connection(
        info,
        query_edges,
        before,
        after,
        first,
        last,
    )


def load_edges(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model: Callable[..., _T],
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> List[Edge[_T]]:

    session = info.context["session"]

    models = load_models(
        session,
        Model,
        id_field,
        before=before,
        after=after,
        first=first,
        last=last,
    )

    nodes = [create_node_from_model(m) for m in models]

    edges = [
        Edge(node=n, cursor=encode_id(getattr(n, id_field))) for n in nodes
    ]

    return edges


def load_models(
    session,
    Model: db_models.ModelType,
    id_field: str,
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
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
    before: Optional[str] = None,
    after: Optional[str] = None,
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
            stmt = stmt.where(getattr(Model, id_field) > decode_id(after))
        stmt = stmt.order_by(getattr(Model, id_field))
        if first is not None:
            stmt = stmt.limit(first)

    elif backward:
        if before:
            stmt = stmt.where(getattr(Model, id_field) < decode_id(before))
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
