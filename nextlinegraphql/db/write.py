from __future__ import annotations

import asyncio
from collections import deque
from logging import getLogger
from typing import TYPE_CHECKING, Deque, List, Union

from sqlalchemy import select

from . import models as db_models
from .db import DB

if TYPE_CHECKING:
    from nextline import Nextline
    from nextline.types import StdoutInfo


async def write_db(nextline: Nextline, db: DB) -> None:
    try:
        await asyncio.gather(
            subscribe_run_info(nextline, db),
            subscribe_trace_info(nextline, db),
            subscribe_prompt_info(nextline, db),
            subscribe_stdout(nextline, db),
        )
    except BaseException:
        logger = getLogger(__name__)
        logger.exception("Exception occurred in writing to DB")
        raise


async def subscribe_run_info(nextline: Nextline, db: DB):
    async for run_info in nextline.subscribe_run_info():
        run_no = run_info.run_no
        with db.session() as session:
            with session.begin():
                model: Union[db_models.Run, None]
                if run_info.state == "initialized":
                    model = db_models.Run(
                        run_no=run_no,
                        state=run_info.state,
                        script=run_info.script,
                    )
                    session.add(model)
                elif run_info.state == "running":
                    stmt = select(db_models.Run).filter_by(run_no=run_no)
                    while not (model := session.execute(stmt).scalar_one_or_none()):
                        await asyncio.sleep(0)
                    model.state = run_info.state
                    model.started_at = run_info.started_at
                elif run_info.state == "finished":
                    stmt = select(db_models.Run).filter_by(run_no=run_no)
                    while not (model := session.execute(stmt).scalar_one_or_none()):
                        await asyncio.sleep(0)
                    model.state = run_info.state
                    model.ended_at = run_info.ended_at
                    model.exception = run_info.exception


async def subscribe_trace_info(nextline: Nextline, db: DB):
    async for trace_info in nextline.subscribe_trace_info():
        with db.session() as session:
            with session.begin():
                model: Union[db_models.Trace, None]
                stmt_runs = select(db_models.Run).filter_by(run_no=trace_info.run_no)
                while not (run := session.execute(stmt_runs).scalar_one_or_none()):
                    await asyncio.sleep(0)
                if trace_info.state == "running":
                    model = db_models.Trace(
                        run_no=trace_info.run_no,
                        trace_no=trace_info.trace_no,
                        state=trace_info.state,
                        thread_no=trace_info.thread_no,
                        task_no=trace_info.task_no,
                        started_at=trace_info.started_at,
                        run=run,
                    )
                    session.add(model)
                elif trace_info.state == "finished":
                    stmt_traces = select(db_models.Trace).filter_by(
                        run_no=trace_info.run_no,
                        trace_no=trace_info.trace_no,
                    )
                    while not (
                        model := session.execute(stmt_traces).scalar_one_or_none()
                    ):
                        await asyncio.sleep(0)
                    model.state = trace_info.state
                    model.ended_at = trace_info.ended_at


async def subscribe_prompt_info(nextline: Nextline, db: DB):
    async for prompt_info in nextline.subscribe_prompt_info():
        if prompt_info.trace_call_end:  # TODO: remove when unnecessary
            continue
        with db.session() as session:
            with session.begin():
                model: Union[db_models.Prompt, None]
                stmt_runs = select(db_models.Run).filter_by(run_no=prompt_info.run_no)
                while not (run := session.execute(stmt_runs).scalar_one_or_none()):
                    await asyncio.sleep(0)
                stmt_traces = select(db_models.Trace).filter_by(
                    run_no=prompt_info.run_no, trace_no=prompt_info.trace_no
                )
                while not (trace := session.execute(stmt_traces).scalar_one_or_none()):
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
                        started_at=prompt_info.started_at,
                        run=run,
                        trace=trace,
                    )
                    session.add(model)
                else:
                    stmt_prompts = select(db_models.Prompt).filter_by(
                        run_no=prompt_info.run_no,
                        prompt_no=prompt_info.prompt_no,
                    )
                    while not (
                        model := session.execute(stmt_prompts).scalar_one_or_none()
                    ):
                        await asyncio.sleep(0)
                    model.open = prompt_info.open
                    model.command = prompt_info.command
                    model.ended_at = prompt_info.ended_at


async def subscribe_stdout(nextline: Nextline, db: DB):

    run_info = None
    stdout_info_list: Deque[StdoutInfo] = deque()
    lock = asyncio.Condition()

    async def f():
        nonlocal stdout_info_list
        async for s in nextline.subscribe_stdout():
            # print(s, file=sys.stderr)
            async with lock:
                stdout_info_list.append(s)

    t = asyncio.create_task(f())

    async for run_info in nextline.subscribe_run_info():
        if not run_info.state == "finished":
            continue
        async with lock:
            to_save: List[StdoutInfo] = []
            while stdout_info_list:
                info = stdout_info_list.popleft()
                if info.run_no < run_info.run_no:
                    continue
                if run_info.run_no < info.run_no:
                    stdout_info_list.appendleft(info)
                    break
                to_save.append(info)
        with db.session() as session:
            with session.begin():
                for info in to_save:
                    stmt_runs = select(db_models.Run).filter_by(run_no=info.run_no)
                    while not (run := session.execute(stmt_runs).scalar_one_or_none()):
                        await asyncio.sleep(0)
                    stmt_traces = select(db_models.Trace).filter_by(
                        run_no=info.run_no, trace_no=info.trace_no
                    )
                    while not (
                        trace := session.execute(stmt_traces).scalar_one_or_none()
                    ):
                        await asyncio.sleep(0)
                    model = db_models.Stdout(
                        run_no=info.run_no,
                        trace_no=info.trace_no,
                        text=info.text,
                        written_at=info.written_at,
                        run=run,
                        trace=trace,
                    )
                    session.add(model)

    t.cancel()
