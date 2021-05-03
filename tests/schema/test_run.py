import sys
import asyncio
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

SUBSCRIBE_THREAD_TASK_STATE = '''
subscription ThreadTaskState(
  $threadId: String!
  $taskId: String
) {
  threadTaskState(threadId: $threadId, taskId: $taskId) {
    prompting
    fileName
    lineNo
  }
}
'''.strip()

##__________________________________________________________________||
async def control_thread_task(client, thread_task_id):
    print(f'control_thread_task({thread_task_id})')

    subscribe_thread_task_state = {
        'id': '1',
        'type': 'start',
        'payload': {
            'variables': thread_task_id,
            'extensions': {},
            'operationName': None,
            'query': SUBSCRIBE_THREAD_TASK_STATE
        }
    }

    mutate_send_pdb_command = {
        'query': MUTATE_SEND_PDB_COMMAND
    }

    headers = {
        'Content-Type:': "application/json"
    }

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_thread_task_state)
        while True:
            resp_json = await ws.receive_json()
            if resp_json['type'] == 'complete':
                break
            state = resp_json['payload']['data']['threadTaskState']

            if state['prompting']:
                mutate_send_pdb_command['variables'] = {
                    **thread_task_id,
                    'command': 'continue'
                }
                resp = await client.post("/", json=mutate_send_pdb_command, headers=headers)

async def control_execution(client):

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

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_thread_task_ids)
        controllers = {}
        while True:
            resp_json = await ws.receive_json()
            if resp_json['type'] == 'complete':
                break
            ids = resp_json['payload']['data']['threadTaskIds']
            ids = [tuple(id_.items()) for id_ in ids] # because a dict cannot be a key of a dict
            prev_ids = list(controllers.keys())
            new_ids = [id_ for id_ in ids if id_ not in prev_ids]
            ended_ids = [id_ for id_ in prev_ids if id_ not in ids]
            for id_ in new_ids:
                task = asyncio.create_task(control_thread_task(client, dict(id_)))
                controllers[id_] = task
            for id_ in ended_ids:
                del controllers[id_]

async def monitor_global_state(client):

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

    async with client.websocket_connect("/") as ws:
        await ws.send_json(subscribe_global_state)
        while True:
            resp_json = await ws.receive_json()
            if resp_json['type'] == 'complete':
                break
            print(resp_json['payload']['data']['globalState'])
            if resp_json['payload']['data']['globalState'] == 'finished':
                return

@pytest.mark.asyncio
async def test_run(snapshot):

    query_global_state = { 'query': QUERY_GLOBAL_STATE }

    mutate_exec = { 'query': MUTATE_EXEC }

    headers = {
        'Content-Type:': "application/json"
    }

    async with TestClient(app) as client:
        resp = await client.post("/", json=query_global_state, headers=headers)
        assert 'initialized' == resp.json()['data']['globalState']

        task_monitor_global_state = asyncio.create_task(monitor_global_state(client))

        resp = await client.post("/", json=mutate_exec, headers=headers)
        assert resp.json()['data']['exec']

        task_control_execution = asyncio.create_task(control_execution(client))

        await task_monitor_global_state

        resp = await client.post("/", json=query_global_state, headers=headers)
        assert 'finished' == resp.json()['data']['globalState']

##__________________________________________________________________||
