import asyncio
from pathlib import Path
from typing import Any

from graphql import ExecutionResult as GraphQLExecutionResult
from nextline import Nextline
from nextline.utils import agen_with_wait

from nextlinegraphql.plugins.ctrl import example_script as example_script_module
from nextlinegraphql.plugins.ctrl.graphql import (
    MUTATE_EXEC,
    MUTATE_SEND_PDB_COMMAND,
    QUERY_CONTINUOUS_ENABLED,
    QUERY_RUN_NO,
    QUERY_SOURCE_LINE,
    QUERY_STATE,
    QUERY_TRACE_IDS,
    SUBSCRIBE_CONTINUOUS_ENABLED,
    SUBSCRIBE_PROMPTING,
    SUBSCRIBE_RUN_NO,
    SUBSCRIBE_STATE,
    SUBSCRIBE_TRACE_IDS,
)
from tests.plugins.ctrl.schema.conftest import Schema

EXAMPLE_SCRIPT_PATH = Path(example_script_module.__file__).parent / 'script.py'
example_script = EXAMPLE_SCRIPT_PATH.read_text()


async def test_schema(schema: Schema) -> None:
    nextline = Nextline(example_script, trace_modules=True, trace_threads=True)
    context = {'nextline': nextline}
    task_subscribe_run_no = asyncio.create_task(
        _subscribe_run_no(schema, context=context)
    )
    task_subscribe_continuous_enabled = asyncio.create_task(
        _subscribe_continuous_enabled(schema, context=context)
    )
    async with nextline:
        task_subscribe_state = asyncio.create_task(
            _subscribe_state(schema, context=context)
        )

        result = await schema.execute(QUERY_STATE, context_value=context)
        assert (data := result.data)
        assert 'initialized' == data['ctrl']['state']

        await asyncio.sleep(0.01)

        task_control_execution = asyncio.create_task(
            _control_execution(schema, context=context)
        )

        await asyncio.sleep(0.01)

        result = await schema.execute(MUTATE_EXEC, context_value=context)
        assert (data := result.data)
        assert data['ctrl']['exec']

        result = await schema.execute(QUERY_RUN_NO, context_value=context)
        assert (data := result.data)
        assert 1 == data['ctrl']['runNo']

        result = await schema.execute(QUERY_TRACE_IDS, context_value=context)
        assert (data := result.data)
        data['ctrl']['traceIds']

        result = await schema.execute(QUERY_CONTINUOUS_ENABLED, context_value=context)
        assert (data := result.data)
        assert False is data['ctrl']['continuousEnabled']

        states, *_ = await asyncio.gather(
            task_subscribe_state,
            task_control_execution,
        )

        await task_control_execution

        assert ['initialized', 'running', 'finished'] == states

        result = await schema.execute(QUERY_STATE, context_value=context)
        assert (data := result.data)
        assert 'finished' == data['ctrl']['state']

    run_nos = await task_subscribe_run_no
    assert [1] == run_nos

    continuous_enabled = await task_subscribe_continuous_enabled
    assert [False] == continuous_enabled


async def _subscribe_state(schema: Schema, context: Any) -> list[str]:
    ret = []
    sub = await schema.subscribe(SUBSCRIBE_STATE, context_value=context)
    assert hasattr(sub, '__aiter__')
    async for result in sub:
        assert (data := result.data)
        state = data['ctrlState']
        ret.append(state)
        if state == 'finished':
            break
    return ret


async def _subscribe_run_no(schema: Schema, context: Any) -> list[int]:
    ret = []
    sub = await schema.subscribe(SUBSCRIBE_RUN_NO, context_value=context)
    assert hasattr(sub, '__aiter__')
    async for result in sub:
        assert (data := result.data)
        run_no = data['ctrlRunNo']
        ret.append(run_no)
    return ret


async def _subscribe_continuous_enabled(schema: Schema, context: Any) -> list[bool]:
    ret = []
    sub = await schema.subscribe(SUBSCRIBE_CONTINUOUS_ENABLED, context_value=context)
    assert hasattr(sub, '__aiter__')
    async for result in sub:
        assert (data := result.data)
        continuous_enabled = data['ctrlContinuousEnabled']
        ret.append(continuous_enabled)
    return ret


async def _control_execution(schema: Schema, context: Any) -> None:
    sub = await schema.subscribe(SUBSCRIBE_TRACE_IDS, context_value=context)
    assert not isinstance(sub, GraphQLExecutionResult)

    agen = agen_with_wait(sub)

    prev_ids = set[int]()
    async for result in agen:
        assert isinstance(result, GraphQLExecutionResult)
        assert (data := result.data)
        trace_ids: list[int] = data['ctrlTraceIds']
        if not (ids := set(trace_ids)):
            break
        new_ids, prev_ids = ids - prev_ids, ids
        tasks = {
            asyncio.create_task(
                _control_trace(schema, context, id_),
            )
            for id_ in new_ids
        }
        _, pending = await agen.asend(tasks)  # type: ignore

    await asyncio.gather(*pending)


async def _control_trace(schema: Schema, context: Any, trace_no: int) -> None:
    to_step = ['script_threading.run()', 'script_asyncio.run()']

    sub = await schema.subscribe(
        SUBSCRIBE_PROMPTING,
        context_value=context,
        variable_values={'traceId': trace_no},
    )
    assert not isinstance(sub, GraphQLExecutionResult)

    async for result in sub:
        assert (data := result.data)
        state = data['ctrlPrompting']
        # e.g. {'fileName': '<string>', 'lineNo': 1, 'prompting': 1, 'traceEvent': 'line'}
        if not state['prompting']:
            continue
        command = 'next'
        if state['traceEvent'] == 'line':
            query_result = await schema.execute(
                QUERY_SOURCE_LINE,
                context_value=context,
                variable_values={
                    'lineNo': state['lineNo'],
                    'fileName': state['fileName'],
                },
            )
            assert (data := query_result.data)
            source_line = data['ctrl']['sourceLine']

            if source_line in to_step:
                command = 'step'

        query_result = await schema.execute(
            MUTATE_SEND_PDB_COMMAND,
            context_value=context,
            variable_values={
                'command': command,
                'promptNo': state['prompting'],
                'traceNo': trace_no,
            },
        )
        assert (data := query_result.data)
        assert data['ctrl']['sendPdbCommand']
