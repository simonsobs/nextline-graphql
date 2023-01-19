from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, List, Optional

import strawberry
from strawberry.tools import merge_types
from strawberry.types import Info

from . import types
from .pagination import Connection

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


def query_source_line(info: Info, line_no: int, file_name: Optional[str]) -> str:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source_line(line_no, file_name)


def query_exception(info: Info) -> Optional[str]:
    nextline: Nextline = info.context["nextline"]
    if exc := nextline.exception():
        return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return None


@strawberry.type
class QueryExec:
    hello: str = strawberry.field(resolver=query_hello)
    state: str = strawberry.field(resolver=query_state)
    run_no: int = strawberry.field(resolver=query_run_no)
    source: List[str] = strawberry.field(resolver=query_source)
    source_line: str = strawberry.field(resolver=query_source_line)
    exception: Optional[str] = strawberry.field(resolver=query_exception)


@strawberry.type
class History:
    runs: Connection[types.RunHistory] = strawberry.field(
        resolver=types.query_connection_run
    )
    traces: Connection[types.TraceHistory] = strawberry.field(
        resolver=types.query_connection_trace
    )
    prompts: Connection[types.PromptHistory] = strawberry.field(
        resolver=types.query_connection_prompt
    )
    stdouts: Connection[types.StdoutHistory] = strawberry.field(
        resolver=types.query_connection_stdout
    )


@strawberry.type
class QueryDB:
    @strawberry.field
    def history(self, info: Info) -> History:
        db = info.context["db"]
        with db.session() as session:
            info.context["session"] = session
            return History()


Query = merge_types('Query', (QueryExec, QueryDB))
