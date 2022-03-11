import asyncio
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Optional, Set
import pytest
from typing import cast
from nextline import Nextline
from nextline.utils import agen_with_wait

from nextlinegraphql.db import init_db, write_db, models as db_models


def test_one(db, run_nextline, statement):
    del run_nextline
    with db() as session:
        session = cast(Session, session)
        runs = session.query(db_models.Run).all()  # type: ignore
        assert 2 == len(runs)
        run = runs[1]
        assert 2 == run.run_no
        assert run.started_at
        assert run.ended_at
        assert statement == run.script
        assert run.exception is None

        traces = session.query(db_models.Trace).all()  # type: ignore
        assert 5 == len(traces)
        run_no = 2
        trace_id = 0
        for trace in traces:
            trace_id += 1
            assert trace_id == trace.trace_id
            assert run_no == trace.run_no
            assert trace.started_at
            assert trace.ended_at

        prompts = session.query(db_models.Prompt).all()  # type: ignore
        assert 58 == len(prompts)
        for prompt in prompts:
            assert run_no == prompt.run_no
            assert prompt.trace_id
            assert prompt.started_at
            assert prompt.line_no
            assert prompt.file_name
            assert prompt.event


@pytest.fixture
def monkey_patch_syspath(monkeypatch):
    pwd = Path(__file__).resolve().parent
    monkeypatch.syspath_prepend(str(pwd))
    yield


@pytest.fixture
def statement(monkey_patch_syspath):
    del monkey_patch_syspath
    pwd = Path(__file__).resolve().parent
    return pwd.joinpath("script.py").read_text()


@pytest.fixture
def db():
    return init_db()


@pytest.fixture
async def run_nextline(db, statement):
    nextline = Nextline(statement)
    task_write = asyncio.create_task(write_db(nextline, db))
    task_control = asyncio.create_task(control_execution(nextline))
    await run_statement(nextline, statement)
    await nextline.close()
    await task_control
    await task_write


async def run_statement(nextline: Nextline, statement: Optional[str] = None):
    await asyncio.sleep(0.01)
    nextline.reset(statement=statement)
    await asyncio.sleep(0.01)
    await nextline.run()
    await asyncio.sleep(0.01)


async def control_execution(nextline: Nextline):
    prev_ids: Set[int] = set()
    agen = agen_with_wait(nextline.subscribe_trace_ids())
    async for ids_ in agen:
        ids = set(ids_)
        new_ids, prev_ids = ids - prev_ids, ids

        tasks = {
            asyncio.create_task(control_trace(nextline, id_))
            for id_ in new_ids
        }
        _, pending = await agen.asend(tasks)

    await asyncio.gather(*pending)


async def control_trace(nextline: Nextline, trace_id):
    file_name = ""
    async for s in nextline.subscribe_prompting(trace_id):
        if not file_name == s.file_name:
            file_name = s.file_name
            assert nextline.get_source(file_name)
        if s.prompting:
            command = "next"
            if s.trace_event == "line":
                line = nextline.get_source_line(
                    line_no=s.line_no,
                    file_name=s.file_name,
                )
                command = find_command(line) or command
            await asyncio.sleep(0.01)
            nextline.send_pdb_command(trace_id, command)


def find_command(line: str) -> Optional[str]:
    """The Pdb command indicated in a comment

    For example, returns "step" for the line "func()  # step"
    """
    import re

    if not (comment := extract_comment(line)):
        return None
    regex = re.compile(r"^# +(\w+) *$")
    match = regex.search(comment)
    if match:
        return match.group(1)
    return None


def extract_comment(line: str) -> Optional[str]:
    import io
    import tokenize

    comments = [
        val
        for type, val, *_ in tokenize.generate_tokens(
            io.StringIO(line).readline
        )
        if type == tokenize.COMMENT
    ]
    if comments:
        return comments[0]
    return None
