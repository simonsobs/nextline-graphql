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


def create_cursor(o: types.RunHistory):
    return base64.b64encode(f"{o.id}".encode()).decode()


def decode_cursor(cursor: str):
    return int(base64.b64decode(cursor).decode())


def query_all_runs(
    info: Info,
    before: Optional[str] = None,
    after: Optional[str] = None,
    first: Optional[int] = None,
    last: Optional[int] = None,
) -> types.Connection[types.RunHistory]:

    # https://relay.dev/graphql/connections.htm

    forward = after or (first is not None)
    backward = before or (last is not None)

    if forward and backward:
        raise ValueError("Only either after/first or before/last is allowed")

    if forward:
        return query_all_runs_forward(info, after, first)

    if backward:
        return query_all_runs_backward(info, before, last)

    return query_all_runs_all(info)


def query_all_runs_all(info: Info) -> types.Connection[types.RunHistory]:

    session = info.context["session"]
    session = cast(Session, session)

    stmt = select(db_models.Run)
    stmt = stmt.order_by(db_models.Run.id)
    models = session.scalars(stmt)
    objs = [types.RunHistory.from_model(m) for m in models]

    edges = [types.Edge(node=t, cursor=create_cursor(t)) for t in objs]

    page_info = types.PageInfo(
        has_previous_page=False,
        has_next_page=False,
        start_cursor=edges[0].cursor if edges else None,
        end_cursor=edges[-1].cursor if edges else None,
    )

    return types.Connection(page_info=page_info, edges=edges)


def query_all_runs_forward(
    info: Info,
    after: Optional[str] = None,
    first: Optional[int] = None,
) -> types.Connection[types.RunHistory]:

    session = info.context["session"]
    session = cast(Session, session)

    stmt = select(db_models.Run)
    if after:
        stmt = stmt.where(db_models.Run.id > decode_cursor(after))
    stmt = stmt.order_by(db_models.Run.id)

    if first is not None:
        stmt = stmt.limit(first + 1)  # add one for has_next_page

    models = session.scalars(stmt)

    objs = [types.RunHistory.from_model(m) for m in models]

    edges = [types.Edge(node=t, cursor=create_cursor(t)) for t in objs]

    has_previous_page = not not after
    has_next_page = (first is not None) and len(edges) == first + 1

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


def query_all_runs_backward(
    info: Info,
    before: Optional[str] = None,
    last: Optional[int] = None,
) -> types.Connection[types.RunHistory]:

    session = info.context["session"]
    session = cast(Session, session)

    stmt = select(db_models.Run)
    if before:
        stmt = stmt.where(db_models.Run.id < decode_cursor(before))

    if last is None:
        stmt = stmt.order_by(db_models.Run.id)

    else:
        # use subquery to limit from last
        # https://stackoverflow.com/a/12125925/7309855
        subq = stmt.order_by(db_models.Run.id.desc())
        subq = subq.limit(last + 1)  # add one for has_previous_page

        # alias to refer a subquery as an ORM
        # https://docs.sqlalchemy.org/en/20/tutorial/data_select.html#orm-entity-subqueries-ctes
        alias = aliased(db_models.Run, subq.subquery())

        stmt = select(alias).order_by(alias.id)

    models = session.scalars(stmt)

    objs = [types.RunHistory.from_model(m) for m in models]

    edges = [types.Edge(node=t, cursor=create_cursor(t)) for t in objs]

    has_previous_page = (last is not None) and len(edges) == last + 1
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
