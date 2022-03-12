from __future__ import annotations
import sys
import asyncio
import datetime
import traceback
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from typing import TYPE_CHECKING, cast

from . import models as db_models

if TYPE_CHECKING:
    from nextline import Nextline


async def write_db(nextline: Nextline, db) -> None:
    try:
        await asyncio.gather(
            subscribe_run_info(nextline, db),
            subscribe_trace_info(nextline, db),
            subscribe_prompt_info(nextline, db),
        )
    except BaseException as exc:
        # TODO: use logging in a way uvicorn can format
        print(f"{exc.__class__.__name__} in write_db()", file=sys.stderr)
        print(
            "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            ),
            file=sys.stderr,
        )
        raise


async def subscribe_run_info(nextline: Nextline, db):
    async for run_info in nextline.subscribe_run_info():
        run_no = run_info.run_no
        now = datetime.datetime.now()
        with db() as session:
            session = cast(Session, session)
            if run_info.state == "running":
                model = db_models.Run(
                    run_no=run_no,
                    state=run_info.state,
                    started_at=now,
                    script=run_info.script,
                )
                session.add(model)
            elif run_info.state == "finished":
                stmt = select(db_models.Run).filter_by(run_no=run_no)
                model = session.execute(stmt).scalar_one()
                model.state = run_info.state
                model.ended_at = now
                model.exception = run_info.exception
            session.commit()


async def subscribe_trace_info(nextline: Nextline, db):
    async for trace_info in nextline.subscribe_trace_info():
        now = datetime.datetime.now()
        with db() as session:
            session = cast(Session, session)
            stmt = select(db_models.Run).filter_by(run_no=trace_info.run_no)
            while not (run := session.execute(stmt).scalar_one_or_none()):
                await asyncio.sleep(0)
            if trace_info.state == "running":
                model = db_models.Trace(
                    run_no=trace_info.run_no,
                    trace_no=trace_info.trace_no,
                    state=trace_info.state,
                    thread_no=trace_info.thread_no,
                    task_no=trace_info.task_no,
                    started_at=now,
                    run=run,
                )
                session.add(model)
            elif trace_info.state == "finished":
                stmt = select(db_models.Trace).filter_by(
                    run_no=trace_info.run_no,
                    trace_no=trace_info.trace_no,
                )
                model = session.execute(stmt).scalar_one()
                model.state = trace_info.state
                model.ended_at = now
            session.commit()


async def subscribe_prompt_info(nextline: Nextline, db):
    async for prompt_info in nextline.subscribe_prompt_info():
        now = datetime.datetime.now()
        with db() as session:
            session = cast(Session, session)
            stmt = select(db_models.Run).filter_by(run_no=prompt_info.run_no)
            while not (run := session.execute(stmt).scalar_one_or_none()):
                await asyncio.sleep(0)
            stmt = select(db_models.Trace).filter_by(
                run_no=prompt_info.run_no, trace_no=prompt_info.trace_no
            )
            while not (trace := session.execute(stmt).scalar_one_or_none()):
                await asyncio.sleep(0)
            if prompt_info.open:
                model = db_models.Prompt(
                    run_no=prompt_info.run_no,
                    trace_no=prompt_info.trace_no,
                    prompt_no=prompt_info.prompt_no,
                    open=prompt_info.open,
                    event=prompt_info.event,
                    file_name=prompt_info.file_name,
                    line_no=prompt_info.line_no,
                    stdout=prompt_info.stdout,
                    started_at=now,
                    run=run,
                    trace=trace,
                )
                session.add(model)
            else:
                stmt = select(db_models.Prompt).filter_by(
                    run_no=prompt_info.run_no,
                    prompt_no=prompt_info.prompt_no,
                )
                model = session.execute(stmt).scalar_one()
                model.open = prompt_info.open
                model.command = prompt_info.command
                model.ended_at = now
            session.commit()
