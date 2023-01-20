from __future__ import annotations

import strawberry
from strawberry.types import Info

from . import types
from .pagination import Connection


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
