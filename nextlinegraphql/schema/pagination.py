from __future__ import annotations
from functools import partial
import base64
from strawberry.types import Info
from sqlalchemy.future import select
from sqlalchemy.orm import Session, aliased
from typing import Optional, cast

from . import types
from ..db import models as db_models


def encode_id(id: int) -> str:
    return base64.b64encode(f"{id}".encode()).decode()


def decode_id(cursor: str) -> int:
    return int(base64.b64decode(cursor).decode())


def load_connection(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model,
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
):
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


def query_connection(
    info: Info,
    query_edges,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
):

    # https://relay.dev/graphql/connections.htm

    forward = after or (first is not None)
    backward = before or (last is not None)

    if forward and backward:
        raise ValueError("Only either after/first or before/last is allowed")

    if forward:
        if first is not None:
            first += 1  # add one for has_next_page

        edges = query_edges(info=info, after=after, first=first)

        has_previous_page = not not after
        has_next_page = (first is not None) and len(edges) == first

        if has_next_page:
            edges = edges[:-1]

    elif backward:
        if last is not None:
            last += 1  # add one for has_previous_page

        edges = query_edges(info=info, before=before, last=last)

        has_previous_page = (last is not None) and len(edges) == last
        has_next_page = not not before

        if has_previous_page:
            edges = edges[1:]

    else:
        edges = query_edges(info)
        has_previous_page = False
        has_next_page = False

    start_cursor = edges[0].cursor if edges else None
    end_cursor = edges[-1].cursor if edges else None

    page_info = types.PageInfo(
        has_previous_page=has_previous_page,
        has_next_page=has_next_page,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
    )

    return types.Connection(page_info=page_info, edges=edges)


def load_edges(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model,
    *,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
):
    forward = after or (first is not None)
    backward = before or (last is not None)

    if forward and backward:
        raise ValueError("Only either after/first or before/last is allowed")

    if forward:
        return load_edges_forward(
            info, Model, id_field, create_node_from_model, after, first
        )

    if backward:
        return load_edges_backward(
            info, Model, id_field, create_node_from_model, before, last
        )

    return load_edges_all(info, Model, id_field, create_node_from_model)


def load_edges_all(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model,
):

    session = info.context["session"]
    session = cast(Session, session)

    stmt = select(Model)
    stmt = stmt.order_by(getattr(Model, id_field))
    models = session.scalars(stmt)
    nodes = [create_node_from_model(m) for m in models]

    edges = [
        types.Edge(node=n, cursor=encode_id(getattr(n, id_field)))
        for n in nodes
    ]

    return edges


def load_edges_forward(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model,
    after: Optional[str] = None,
    first: Optional[int] = None,
):
    session = info.context["session"]
    session = cast(Session, session)

    stmt = select(Model)
    if after:
        stmt = stmt.where(getattr(Model, id_field) > decode_id(after))
    stmt = stmt.order_by(getattr(Model, id_field))

    if first is not None:
        stmt = stmt.limit(first)

    models = session.scalars(stmt)

    nodes = [create_node_from_model(m) for m in models]

    edges = [
        types.Edge(node=n, cursor=encode_id(getattr(n, id_field)))
        for n in nodes
    ]

    return edges


def load_edges_backward(
    info: Info,
    Model: db_models.ModelType,
    id_field: str,
    create_node_from_model,
    before: Optional[str] = None,
    last: Optional[int] = None,
):

    session = info.context["session"]
    session = cast(Session, session)

    stmt = select(Model)
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

    models = session.scalars(stmt)

    nodes = [create_node_from_model(m) for m in models]

    edges = [
        types.Edge(node=n, cursor=encode_id(getattr(n, id_field)))
        for n in nodes
    ]

    return edges
