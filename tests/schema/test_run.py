import sys
from async_asgi_testclient import TestClient

import pytest

from nextlinegraphql import app

##__________________________________________________________________||
MUTATE_EXEC = '''
mutation Exec {
  exec
}
'''.strip()


MUTATE_SEND_PDB_COMMAND = '''
mutation SendPdbCommand(
  $threadId: String!
  $taskId: String
  $command: String!
) {
  sendPdbCommand(threadId: $threadId, taskId: $taskId, command: $command)
}
'''.strip()

SUBSCRIBE_STATE = '''
subscription State {
  state {
    globalState
    nthreads
    threads {
      threadId
      tasks {
        taskId
        prompting
        fileName
        lineNo
      }
    }
  }
}
'''.strip()

QUERY_STATE = '''
{
  state {
    globalState
    nthreads
    threads {
      threadId
      tasks {
        taskId
        prompting
        fileName
        lineNo
      }
    }
  }
}
'''.strip()

QUERY_GLOBAL_STATE = '''
query GlobalState {
  globalState
}
'''.strip()

SUBSCRIBE_GLOBAL_STATE = '''
subscription GlobalState {
  globalState
}
'''.strip()

SUBSCRIBE_THREAD_TASK_IDS = '''
subscription ThreadTaskIds {
  threadTaskIds {
    threadId
    taskId
  }
}
'''.strip()

##__________________________________________________________________||
async def prompting_thread_tasks(ws):
    prompting_counts_prev = {} # key (thread_id, task_id)
    while True:
        resp_json = await ws.receive_json()
        state = resp_json['payload']['data']['state']
        if not state['globalState'] == 'running':
            return
        threads = state['threads']
        prompting_counts = {(th['threadId'], ta['taskId']): ta['prompting'] for th in threads for ta in th['tasks']}
        thread_tasks = []
        for thread_id_task_id in prompting_counts:
            if thread_id_task_id in prompting_counts_prev:
                if prompting_counts[thread_id_task_id] > prompting_counts_prev[thread_id_task_id]:
                    thread_tasks.append(thread_id_task_id)
            else:
                thread_tasks.append(thread_id_task_id)
        if thread_tasks:
            yield thread_tasks
        prompting_counts_prev = prompting_counts.copy()

@pytest.mark.asyncio
async def test_run(snapshot):

    query_global_state = { 'query': QUERY_GLOBAL_STATE }

    subscribe_global_state = {
        'id': '1',
        'type': 'start',
        'payload': {
            'variables': {},
            'extensions': {},
            'operationName': None,
            'query': SUBSCRIBE_GLOBAL_STATE
        }
    }

    subscribe_state = {
        'id': '1',
        'type': 'start',
        'payload': {
            'variables': {},
            'extensions': {},
            'operationName': None,
            'query': SUBSCRIBE_STATE
        }
    }

    subscribe_thread_task_ids = {
        'id': '1',
        'type': 'start',
        'payload': {
            'variables': {},
            'extensions': {},
            'operationName': None,
            'query': SUBSCRIBE_THREAD_TASK_IDS
        }
    }

    query_state = { 'query': QUERY_STATE }

    mutate_exec = { 'query': MUTATE_EXEC }

    mutate_send_pdb_command = {
        'query': MUTATE_SEND_PDB_COMMAND
    }

    headers = {
        'Content-Type:': "application/json"
    }

    async with TestClient(app) as client:
        resp = await client.post("/", json=query_state, headers=headers)
        assert 'initialized' == resp.json()['data']['state']['globalState']

        resp = await client.post("/", json=query_global_state, headers=headers)
        assert 'initialized' == resp.json()['data']['globalState']

        async with client.websocket_connect("/") as ws_global_state, \
                   client.websocket_connect("/") as ws_thread_task_ids, \
                   client.websocket_connect("/") as ws:

            await ws_global_state.send_json(subscribe_global_state)
            resp_json = await ws_global_state.receive_json()
            assert 'initialized' == resp_json['payload']['data']['globalState']

            await ws_thread_task_ids.send_json(subscribe_thread_task_ids)
            # print('here')
            # resp_json = await ws_thread_task_ids.receive_json()
            # print('here')
            # from pprint import pprint
            # pprint(resp_json['payload']['data'])

            await ws.send_json(subscribe_state)
            # resp_json = await ws.receive_json()
            # state = resp_json['payload']['data']['state']
            # assert state['globalState'] == 'initialized'

            resp = await client.post("/", json=mutate_exec, headers=headers)
            assert resp.json()['data']['exec']

            resp_json = await ws_global_state.receive_json()
            assert 'running' == resp_json['payload']['data']['globalState']

            niterations = 0
            all_thread_tasks = set()
            async for thread_tasks in prompting_thread_tasks(ws):
                niterations += 1
                all_thread_tasks.update(thread_tasks)
                for thread_id, task_id in thread_tasks:
                    mutate_send_pdb_command['variables'] = {
                        'threadId': thread_id,
                        'taskId': task_id,
                        'command': 'continue'
                    }
                    resp = await client.post("/", json=mutate_send_pdb_command, headers=headers)
            assert niterations >= 4
            assert len(all_thread_tasks) == 5

            resp_json = await ws_global_state.receive_json()
            assert 'running' == resp_json['payload']['data']['globalState']

        resp = await client.post("/", json=query_state, headers=headers)
        assert 'finished' == resp.json()['data']['state']['globalState']

        resp = await client.post("/", json=query_global_state, headers=headers)
        assert 'finished' == resp.json()['data']['globalState']

##__________________________________________________________________||
