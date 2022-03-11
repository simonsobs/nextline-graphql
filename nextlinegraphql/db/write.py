from __future__ import annotations
import sys
import asyncio
import datetime
import traceback
from sqlalchemy.orm import Session

from typing import TYPE_CHECKING, Set, cast

from nextline.utils import agen_with_wait

from . import models as db_models

if TYPE_CHECKING:
    from nextline import Nextline


async def write_db(nextline: Nextline, db) -> None:
    try:
        await asyncio.gather(
            subscribe_state(nextline, db),
            subscribe_trace_ids(nextline, db),
        )
    except BaseException as exc:
        # TODO: use logging in a way uvicorn can format
        print(f"{exc.__class__.__name__} in write_db()", file=sys.stderr)
        print(exc, file=sys.stderr)

        raise


async def subscribe_state(nextline: Nextline, db):
    async for state_name in nextline.subscribe_state():
        if state_name == "closed":
            continue
        run_no = nextline.run_no
        now = datetime.datetime.now()
        with db() as session:
            session = cast(Session, session)
            run = (
                session.query(db_models.Run)  # type: ignore
                .filter_by(run_no=run_no)
                .one_or_none()
            )
            if run is None:
                run = db_models.Run(  # type: ignore
                    run_no=run_no,
                    script=nextline.statement,
                )
                session.add(run)
            run.state = state_name
            if state_name == "running":
                run.started_at = now
            if state_name == "exited":
                run.ended_at = now
            if state_name == "finished":
                exc = nextline.exception()
                if exc:
                    run.exception = "".join(
                        traceback.format_exception(
                            type(exc), exc, exc.__traceback__
                        )
                    )
            session.commit()


async def subscribe_trace_ids(nextline: Nextline, db) -> None:
    ids: Set[int] = set()
    pending: Set[asyncio.Task] = set()
    agen = agen_with_wait(nextline.subscribe_trace_ids())
    async for ids_ in agen:
        ids_ = set(ids_)
        started = ids_ - ids
        ended = ids - ids_
        ids = ids_
        tasks = {
            asyncio.create_task(subscribe_prompting(nextline, db, id_))
            for id_ in started
        }
        _, pending = await agen.asend(tasks)
        run_no = nextline.run_no
        now = datetime.datetime.now()
        with db() as session:
            session = cast(Session, session)
            for id_ in started:
                trace = db_models.Trace(  # type: ignore
                    trace_id=id_,
                    run_no=run_no,
                    started_at=now,
                )
                session.add(trace)
            for id_ in ended:
                trace = (
                    session.query(db_models.Trace)  # type: ignore
                    .filter_by(run_no=run_no, trace_id=id_)
                    .one()
                )
                trace.ended_at = now
            session.commit()

    await asyncio.gather(*pending)


async def subscribe_prompting(nextline: Nextline, db, trace_id: int) -> None:
    async for s in nextline.subscribe_prompting(trace_id):
        if not s.prompting:
            continue
        run_no = nextline.run_no
        now = datetime.datetime.now()
        with db() as session:
            session = cast(Session, session)
            prompt = db_models.Prompt(  # type: ignore
                run_no=run_no,
                trace_id=trace_id,
                prompt_no=s.prompting,
                started_at=now,
                file_name=s.file_name,
                line_no=s.line_no,
                event=s.trace_event,
            )
            session.add(prompt)
            session.commit()
