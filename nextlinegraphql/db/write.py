from __future__ import annotations
import asyncio
import datetime
import traceback

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nextline import Nextline
    from . import Db


async def write_db(nextline: Nextline, db: Db) -> None:
    t = asyncio.create_task(subscribe_state(nextline, db))
    await t


async def subscribe_state(nextline: Nextline, db: Db):
    async for state_name in nextline.subscribe_state():
        run_no = nextline.run_no
        now = datetime.datetime.now()
        with db.Session.begin() as session:
            state_change = db.models.StateChange(
                name=state_name, datetime=now, run_no=run_no
            )
            run = (
                session.query(db.models.Run)
                .filter_by(run_no=run_no)
                .one_or_none()
            )
            if run is None:
                run = db.models.Run(run_no=run, script=nextline.statement)
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
