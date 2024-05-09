from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd / 'mutations'
MUTATE_EXEC = (sub / 'Exec.gql').read_text()
MUTATE_RESET = (sub / 'Reset.gql').read_text()
MUTATE_SEND_PDB_COMMAND = (sub / 'SendPdbCommand.gql').read_text()
MUTATE_RUN_AND_CONTINUE = (sub / 'RunAndContinue.gql').read_text()
MUTATE_LOAD_EXAMPLE_SCRIPT = (sub / 'LoadExampleScript.gql').read_text()

sub = pwd / 'queries'
QUERY_STATE = (sub / 'State.gql').read_text()
QUERY_EXCEPTION = (sub / 'Exception.gql').read_text()
QUERY_SOURCE = (sub / 'Source.gql').read_text()
QUERY_SOURCE_LINE = (sub / 'SourceLine.gql').read_text()

sub = pwd / 'subscriptions'
SUBSCRIBE_COUNTER = (sub / 'Counter.gql').read_text()
SUBSCRIBE_STATE = (sub / 'State.gql').read_text()
SUBSCRIBE_STDOUT = (sub / 'Stdout.gql').read_text()
SUBSCRIBE_TRACE_IDS = (sub / 'TraceIds.gql').read_text()
SUBSCRIBE_PROMPTING = (sub / 'Prompting.gql').read_text()
