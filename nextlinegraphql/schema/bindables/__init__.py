from __future__ import annotations

import sys
import io
import asyncio
import traceback
from ariadne import ScalarType, QueryType, MutationType, SubscriptionType

from typing import (
    TYPE_CHECKING,
    AsyncGenerator,
    Callable,
    Union,
    Iterable,
    TextIO,
)

from nextline.utils import QueueDist

from ...nl import run_nextline, reset_nextline, close_nextline
from ...db import Db

if TYPE_CHECKING:
    from nextline import Nextline


##__________________________________________________________________||
datetime_scalar = ScalarType("Datetime")


@datetime_scalar.serializer
def serialize_datetime(value):
    print(value)
    return value.isoformat()


##__________________________________________________________________||
query = QueryType()


@query.field("hello")
async def resolve_hello(_, info):
    request = info.context["request"]
    user_agent = request.headers.get("user-agent", "guest")
    return "Hello, %s!" % user_agent


@query.field("helloDb")
async def resolve_hello_db(_, info):
    db = info.context["db"]
    with db.Session.begin() as session:
        model = session.query(db.models.Hello).one_or_none()
        if model is None:
            return None
        return model.message


@query.field("stateChanges")
async def resolve_state_changes(_, info):
    db = info.context["db"]
    with db.Session.begin() as session:
        models = session.query(db.models.StateChange).all()
        return [
            {"name": m.name, "datetime": m.datetime, "runNo": m.run_no}
            for m in models
        ]


@query.field("runs")
async def resolve_runs(_, info):
    db: Db = info.context["db"]
    with db.Session.begin() as session:
        runs: Iterable[db.models.Run] = session.query(db.models.Run)
        return [
            {
                "runNo": run.run_no,
                "state": run.state,
                "startedAt": run.started_at,
                "endedAt": run.ended_at,
                "script": run.script,
                "exception": run.exception,
            }
            for run in runs
        ]


@query.field("globalState")
async def resolve_state(_, info):
    nextline: Nextline = info.context["nextline"]
    return nextline.state


@query.field("runNo")
async def resolve_run_no(_, info):
    nextline: Nextline = info.context["nextline"]
    return nextline.run_no


@query.field("source")
async def resolve_source(_, info, fileName=None):
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source(fileName)


@query.field("sourceLine")
async def resolve_source_line(_, info, lineNo, fileName=None):
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source_line(lineNo, fileName)


@query.field("exception")
async def resolve_exception(_, info):
    nextline: Nextline = info.context["nextline"]
    exc = nextline.exception()
    if not exc:
        return
    ret = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    return ret


##__________________________________________________________________||
subscription = SubscriptionType()


@subscription.source("counter")
async def counter_generator(obj, info):
    for i in range(5):
        await asyncio.sleep(1)
        yield i


@subscription.field("counter")
def counter_resolver(count, info):
    return count + 1


@subscription.source("globalState")
async def state_generator(_, info):
    nextline: Nextline = info.context["nextline"]
    async for s in nextline.subscribe_state():
        # if s == 'finished':
        #     print('finished', nextline.exception())
        #     nextline.result()
        yield s


@subscription.field("globalState")
def state_resolver(state, info):
    return state


@subscription.source("runNo")
async def run_no_generator(_, info):
    nextline: Nextline = info.context["nextline"]
    async for s in nextline.subscribe_run_no():
        yield s


@subscription.field("runNo")
def run_no_resolver(run_no, info):
    return run_no


@subscription.source("traceIds")
async def trace_ids_generator(_, info):
    nextline: Nextline = info.context["nextline"]
    async for y in nextline.subscribe_trace_ids():
        yield y


@subscription.field("traceIds")
def trace_ids_resolver(obj, info):
    return obj


@subscription.source("traceState")
async def trace_state_generator(_, info, traceId):
    trace_id = traceId
    nextline: Nextline = info.context["nextline"]
    async for y in nextline.subscribe_prompting(trace_id):
        y = {
            "prompting": y.prompting,
            "fileName": y.file_name,
            "lineNo": y.line_no,
            "traceEvent": y.trace_event,
        }
        yield y


@subscription.field("traceState")
def trace_state_resolver(obj, info, traceId):
    return obj


@subscription.source("stdout")
async def stdout_generator(_, info):
    nextline: Nextline = info.context["nextline"]
    async for v in subscribe_stdout():
        if nextline.state == "running":
            yield v


@subscription.field("stdout")
def stdout_resolver(stdout, info):
    return stdout


##__________________________________________________________________||
mutation = MutationType()


@mutation.field("exec")
async def resolve_exec(_, info):
    # print(_)
    # print(info)
    await run_nextline()
    return True


@mutation.field("reset")
async def resolve_reset(_, info, statement=None):
    reset_nextline(statement=statement)
    return True


@mutation.field("close")
async def resolve_close(_, info):
    await close_nextline()
    return True


@mutation.field("sendPdbCommand")
async def resolve_send_pdb_command(_, info, traceId, command):
    trace_id = traceId
    nextline: Nextline = info.context["nextline"]
    nextline.send_pdb_command(trace_id, command)
    return True


@mutation.field("updateHelloDbMessage")
async def resolve_update_hello_db_message(_, info, message):
    db = info.context["db"]
    with db.Session.begin() as session:
        model = session.query(db.models.Hello).one_or_none()
        if model is None:
            model = db.models.Hello(message=message)
            session.add(model)
        else:
            model.message = message
        session.commit()
    return True


##__________________________________________________________________||
AGenStr = AsyncGenerator[str, None]


class IOSubscription(io.TextIOWrapper):
    def __init__(self, src: TextIO):
        """Make output stream subscribable

        The src needs to be replaced with the instance of this class. For
        example, if the src is stdout,
            sys.stdout = IOSubscription(sys.stdout)
        """
        self._queue = QueueDist()
        self._src = src

    def write(self, s: str) -> int:
        self._queue.put(s)
        return self._src.write(s)

    def flush(self):
        pass

    async def subscribe(self) -> AGenStr:
        async for y in self._queue.subscribe():
            yield y


def create_subscribe_stdout() -> Callable[[], AGenStr]:
    stream: Union[IOSubscription, None] = None

    async def subscribe_stdout() -> AGenStr:
        nonlocal stream
        if not stream:
            stream = sys.stdout = IOSubscription(sys.stdout)
        async for y in stream.subscribe():
            yield y

    return subscribe_stdout


subscribe_stdout = create_subscribe_stdout()

##__________________________________________________________________||
bindables = [query, mutation, subscription, datetime_scalar]

##__________________________________________________________________||
