
##__________________________________________________________________||
QUERY_GLOBAL_STATE = '''
query GlobalState {
  globalState
}
'''.strip()

QUERY_SOURCE = '''
query Source($fileName: String) {
  source(fileName: $fileName)
}
'''.strip()

QUERY_SOURCE_LINE = '''
query SourceLine(
  $lineNo: Int!
  $fileName: String
) {
  sourceLine(lineNo: $lineNo, fileName: $fileName)
}
'''.strip()

QUERY_EXCEPTION = '''
query Exception {
  exception
}
'''.strip()

##__________________________________________________________________||
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
    traceEvent
  }
}
'''.strip()

##__________________________________________________________________||
MUTATE_EXEC = '''
mutation Exec {
  exec
}
'''.strip()


MUTATION_RESET = '''
mutation Reset($statement: String) {
  reset(statement: $statement)
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

