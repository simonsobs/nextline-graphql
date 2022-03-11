from __future__ import annotations
import datetime
import base64
import strawberry
from typing import Optional


@strawberry.type
class StateChange:
    name: str
    datetime: datetime.datetime
    run_no: int


@strawberry.type
class RunHistory:
    run_no: int
    state: Optional[str] = None
    started_at: Optional[datetime.date] = None
    ended_at: Optional[datetime.date] = None
    script: Optional[str] = None
    exception: Optional[str] = None

    @strawberry.field
    def id(self) -> strawberry.ID:
        s = f"{self.__class__.__name__}:{self.run_no}"
        return strawberry.ID(base64.b64encode(s.encode()).decode())


@strawberry.type
class TraceHistory:
    run_no: int
    trace_id: int
    started_at: datetime.date
    ended_at: Optional[datetime.date] = None

    @strawberry.field
    def id(self) -> strawberry.ID:
        s = f"{self.__class__.__name__}:{self.run_no}-{self.trace_id}"
        return strawberry.ID(base64.b64encode(s.encode()).decode())


@strawberry.type
class PromptHistory:
    run_no: int
    trace_id: int
    prompt_no: int
    event: str
    started_at: datetime.date
    file_name: Optional[str] = None
    line_no: Optional[int] = None

    @strawberry.field
    def id(self) -> strawberry.ID:
        s = f"{self.__class__.__name__}:{self.run_no}-{self.prompt_no}"
        return strawberry.ID(base64.b64encode(s.encode()).decode())


@strawberry.type
class PromptingData:
    prompting: int
    file_name: str
    line_no: int
    trace_event: str
