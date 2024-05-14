import asyncio
from pathlib import Path
from typing import Any

from graphql import ExecutionResult as GraphQLExecutionResult
from nextline import Nextline
from nextline.utils import agen_with_wait
from strawberry import Schema

from nextlinegraphql.plugins.ctrl import example_script as example_script_module
from nextlinegraphql.plugins.ctrl.graphql import (
    MUTATE_EXEC,
    MUTATE_SEND_PDB_COMMAND,
    QUERY_SOURCE_LINE,
    QUERY_STATE,
    SUBSCRIBE_PROMPTING,
    SUBSCRIBE_STATE,
    SUBSCRIBE_TRACE_IDS,
)
from nextlinegraphql.plugins.ctrl.schema import Mutation, Query, Subscription

EXAMPLE_SCRIPT_PATH = Path(example_script_module.__file__).parent / 'script.py'
example_script = EXAMPLE_SCRIPT_PATH.read_text()


async def test_schema() -> None:
    schema = Schema(query=Query, mutation=Mutation, subscription=Subscription)
    assert schema
    nextline = Nextline(example_script, trace_modules=True, trace_threads=True)
    async with nextline:
        context = {'nextline': nextline}

        task_subscribe_state = asyncio.create_task(
            _subscribe_state(schema, context=context)
        )

        result = await schema.execute(QUERY_STATE, context_value=context)
        assert (data := result.data)
        assert 'initialized' == data['state']

        await asyncio.sleep(0.01)

        task_control_execution = asyncio.create_task(
            _control_execution(schema, context=context)
        )

        await asyncio.sleep(0.01)

        result = await schema.execute(MUTATE_EXEC, context_value=context)
        assert (data := result.data)
        assert data['exec']

        states, *_ = await asyncio.gather(
            task_subscribe_state,
            task_control_execution,
        )

        assert ['initialized', 'running', 'finished'] == states

        result = await schema.execute(QUERY_STATE, context_value=context)
        assert (data := result.data)
        assert 'finished' == data['state']


async def _subscribe_state(schema: Schema, context: Any) -> list[str]:
    ret = []
    sub = await schema.subscribe(SUBSCRIBE_STATE, context_value=context)
    assert hasattr(sub, '__aiter__')
    async for result in sub:
        assert (data := result.data)
        state = data['state']
        ret.append(state)
        if state == 'finished':
            break
    return ret


async def _control_execution(schema: Schema, context: Any) -> None:
    sub = await schema.subscribe(SUBSCRIBE_TRACE_IDS, context_value=context)
    assert not isinstance(sub, GraphQLExecutionResult)

    agen = agen_with_wait(sub)

    prev_ids = set[int]()
    async for result in agen:
        assert isinstance(result, GraphQLExecutionResult)
        assert (data := result.data)
        trace_ids: list[int] = data['traceIds']
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
        state = data['prompting']
        # e.g. {'fileName': '<string>', 'lineNo': 1, 'prompting': 1, 'traceEvent': 'line'}
        if state['prompting']:
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
                source_line = data['sourceLine']

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
            assert data['sendPdbCommand']
