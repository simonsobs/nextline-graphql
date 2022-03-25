from __future__ import annotations
import base64
import traceback
import strawberry
from strawberry.types import Info
from sqlalchemy.future import select
from sqlalchemy.orm import Session, aliased
from typing import TYPE_CHECKING, List, Optional, cast

from . import types
from ..db import models as db_models

if TYPE_CHECKING:
    from nextline import Nextline


def query_hello(info: Info) -> str:
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent


def query_state(info: Info) -> str:
    nextline: Nextline = info.context["nextline"]
    return nextline.state


def query_run_no(info: Info) -> int:
    nextline: Nextline = info.context["nextline"]
    return nextline.run_no


def query_source(info: Info, file_name: Optional[str] = None) -> List[str]:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source(file_name)


def query_source_line(
    info: Info, line_no: int, file_name: Optional[str]
) -> str:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source_line(line_no, file_name)


def query_exception(info: Info) -> Optional[str]:
    nextline: Nextline = info.context["nextline"]
    if exc := nextline.exception():
        return "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )
    return None


def query_runs(info: Info) -> List[types.RunHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Run))
    return [types.RunHistory.from_model(m) for m in models]


def query_traces(info: Info) -> List[types.TraceHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Trace))
    return [types.TraceHistory.from_model(m) for m in models]


def query_prompt(info: Info) -> List[types.PromptHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Prompt))
    return [types.PromptHistory.from_model(m) for m in models]


def query_stdouts(info: Info) -> List[types.StdoutHistory]:
    session = info.context["session"]
    session = cast(Session, session)
    models = session.scalars(select(db_models.Stdout))
    return [types.StdoutHistory.from_model(m) for m in models]


def encode_id(id: int) -> str:
    return base64.b64encode(f"{id}".encode()).decode()


def decode_id(cursor: str) -> int:
    return int(base64.b64decode(cursor).decode())


def query_all_runs(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> types.Connection[types.RunHistory]:

    Model = db_models.Run
    id_field = "id"
    create_node_from_model = types.RunHistory.from_model

    def query_edges(
        info: Info,
        *,
        before: Optional[str] = None,
        after: Optional[str] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ):
        return get_edges(
            info,
            Model,
            id_field,
            create_node_from_model,
            before=before,
            after=after,
            first=first,
            last=last,
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
        return query_connection_forward(
            info,
            query_edges,
            after,
            first,
        )

    if backward:
        return query_connection_backward(
            info,
            query_edges,
            before,
            last,
        )

    return query_connection_all(info, query_edges)


def query_connection_all(info: Info, load_edges):

    edges = load_edges(info)

    page_info = types.PageInfo(
        has_previous_page=False,
        has_next_page=False,
        start_cursor=edges[0].cursor if edges else None,
        end_cursor=edges[-1].cursor if edges else None,
    )

    return types.Connection(page_info=page_info, edges=edges)


def query_connection_forward(
    info: Info,
    load_edges,
    after: Optional[str] = None,
    first: Optional[int] = None,
):

    if first is not None:
        first += 1  # add one for has_next_page

    edges = load_edges(info=info, after=after, first=first)

    has_previous_page = not not after
    has_next_page = (first is not None) and len(edges) == first

    if has_next_page:
        edges = edges[:-1]

    start_cursor = edges[0].cursor if edges else None
    end_cursor = edges[-1].cursor if edges else None

    page_info = types.PageInfo(
        has_previous_page=has_previous_page,
        has_next_page=has_next_page,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
    )

    return types.Connection(page_info=page_info, edges=edges)


def query_connection_backward(
    info: Info,
    load_edges,
    before: Optional[str] = None,
    last: Optional[int] = None,
):

    if last is not None:
        last += 1  # add one for has_previous_page

    edges = load_edges(info=info, before=before, last=last)

    has_previous_page = (last is not None) and len(edges) == last
    has_next_page = not not before

    if has_previous_page:
        edges = edges[1:]

    start_cursor = edges[0].cursor if edges else None
    end_cursor = edges[-1].cursor if edges else None

    page_info = types.PageInfo(
        has_previous_page=has_previous_page,
        has_next_page=has_next_page,
        start_cursor=start_cursor,
        end_cursor=end_cursor,
    )

    return types.Connection(page_info=page_info, edges=edges)


def get_edges(
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
        return get_edges_forward(
            info, Model, id_field, create_node_from_model, after, first
        )

    if backward:
        return get_edges_backward(
            info, Model, id_field, create_node_from_model, before, last
        )

    return get_edges_all(info, Model, id_field, create_node_from_model)


def get_edges_all(
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


def get_edges_forward(
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


def get_edges_backward(
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


@strawberry.type
class History:
    runs: List[types.RunHistory] = strawberry.field(resolver=query_runs)
    traces: List[types.TraceHistory] = strawberry.field(resolver=query_traces)
    prompts: List[types.PromptHistory] = strawberry.field(
        resolver=query_prompt
    )
    stdouts: List[types.StdoutHistory] = strawberry.field(
        resolver=query_stdouts
    )

    all_runs: types.Connection[types.RunHistory] = strawberry.field(
        resolver=query_all_runs
    )


@strawberry.type
class Query:
    hello: str = strawberry.field(resolver=query_hello)
    state: str = strawberry.field(resolver=query_state)
    run_no: int = strawberry.field(resolver=query_run_no)
    source: List[str] = strawberry.field(resolver=query_source)
    source_line: str = strawberry.field(resolver=query_source_line)
    exception: Optional[str] = strawberry.field(resolver=query_exception)

    @strawberry.field
    def history(self, info: Info) -> History:
        db = info.context["db"]
        with db() as session:
            info.context["session"] = session
            return History()
