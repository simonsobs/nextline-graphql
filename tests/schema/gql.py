
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

SUBSCRIBE_TRACE_IDS = '''
subscription TraceIds {
  traceIds
}
'''.strip()

SUBSCRIBE_TRACE_STATE = '''
subscription TraceState(
  $traceId: Int!
) {
  traceState(traceId: $traceId) {
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
  $traceId: Int!
  $command: String!
) {
  sendPdbCommand(traceId: $traceId, command: $command)
}
'''.strip()

