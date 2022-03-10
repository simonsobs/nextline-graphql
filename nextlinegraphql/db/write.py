from __future__ import annotations
import asyncio
import datetime
import traceback

from typing import TYPE_CHECKING, Set

from nextline.utils import agen_with_wait

if TYPE_CHECKING:
    from nextline import Nextline
    from . import Db


async def write_db(nextline: Nextline, db: Db) -> None:
    aws: Set[asyncio.Task] = set()
    aws.add(asyncio.create_task(subscribe_state(nextline, db)))
    aws.add(asyncio.create_task(subscribe_trace_ids(nextline, db)))
    await asyncio.gather(*aws)


async def subscribe_state(nextline: Nextline, db: Db):
    async for state_name in nextline.subscribe_state():
        run_no = nextline.run_no
        now = datetime.datetime.now()
        with db.Session.begin() as session:
            state_change = db.models.StateChange(  # type: ignore
                name=state_name, datetime=now, run_no=run_no
            )
            run = (
                session.query(db.models.Run)  # type: ignore
                .filter_by(run_no=run_no)
                .one_or_none()
            )
            if run is None:
                run = db.models.Run(run_no=run, script=nextline.statement)  # type: ignore
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
            session.add(state_change)
            session.commit()


async def subscribe_trace_ids(nextline: Nextline, db: Db) -> None:
    prev_ids: Set[int] = set()
    agen = agen_with_wait(nextline.subscribe_trace_ids())
    async for ids_ in agen:
        ids = set(ids_)
        new_ids, prev_ids = ids - prev_ids, ids
        tasks = {
            asyncio.create_task(subscribe_prompting(nextline, db, id_))
            for id_ in new_ids
        }
        _, pending = await agen.asend(tasks)

    await asyncio.gather(*pending)


async def subscribe_prompting(
    nextline: Nextline,
    db: Db,
    trace_id: int,
) -> None:
    async for s in nextline.subscribe_prompting(trace_id):
        # print(s)
        pass
