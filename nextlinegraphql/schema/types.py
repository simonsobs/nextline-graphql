# from __future__ import annotations
# strawberry.Private will be compatible with annotations
# https://github.com/strawberry-graphql/strawberry/pull/1684

import datetime
import strawberry
from typing import Optional, Type

from ..db import models as db_models


@strawberry.type
class StateChange:
    name: str
    datetime: datetime.datetime
    run_no: int


@strawberry.type
class RunHistory:
    _model: strawberry.Private[db_models.Run]
    id: int
    run_no: int
    state: Optional[str] = None
    started_at: Optional[datetime.date] = None
    ended_at: Optional[datetime.date] = None
    script: Optional[str] = None
    exception: Optional[str] = None

    @classmethod
    def from_model(cls: Type["RunHistory"], model: db_models.Run):
        return cls(
            _model=model,
            id=model.run_no,
            run_no=model.run_no,
            state=model.state,
            started_at=model.started_at,
            ended_at=model.ended_at,
            script=model.script,
            exception=model.exception,
        )


@strawberry.type
class TraceHistory:
    _model: strawberry.Private[db_models.Trace]
    id: int
    run_no: int
    trace_id: int
    started_at: datetime.date
    ended_at: Optional[datetime.date] = None

    @classmethod
    def from_model(cls: Type["TraceHistory"], model: db_models.Trace):
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            trace_id=model.trace_id,
            started_at=model.started_at,
            ended_at=model.ended_at,
        )


@strawberry.type
class PromptHistory:
    _model: strawberry.Private[db_models.Prompt]
    id: int
    run_no: int
    trace_id: int
    prompt_no: int
    event: str
    started_at: datetime.date
    file_name: Optional[str] = None
    line_no: Optional[int] = None

    @classmethod
    def from_model(cls: Type["PromptHistory"], model: db_models.Prompt):
        return cls(
            _model=model,
            id=model.id,
            run_no=model.run_no,
            trace_id=model.trace_id,
            prompt_no=model.prompt_no,
            started_at=model.started_at,
            file_name=model.file_name,
            line_no=model.line_no,
            event=model.event,
        )


@strawberry.type
class PromptingData:
    prompting: int
    file_name: str
    line_no: int
    trace_event: str
