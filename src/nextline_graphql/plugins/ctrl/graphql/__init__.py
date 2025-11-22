from pathlib import Path

from graphql import parse, print_ast


def read_gql(path: Path | str) -> str:
    '''Load a GraphQL query from a file while checking its syntax.'''

    text = Path(path).read_text()
    parsed = parse(text)
    reformatted = print_ast(parsed)
    return reformatted


pwd = Path(__file__).resolve().parent

sub = pwd / 'mutations'
MUTATE_EXEC = read_gql(sub / 'Exec.gql')
MUTATE_RUN_AND_CONTINUE = read_gql(sub / 'RunAndContinue.gql')
MUTATE_RESET = read_gql(sub / 'Reset.gql')
MUTATE_SEND_PDB_COMMAND = read_gql(sub / 'SendPdbCommand.gql')
MUTATE_INTERRUPT = read_gql(sub / 'Interrupt.gql')
MUTATE_TERMINATE = read_gql(sub / 'Terminate.gql')
MUTATE_KILL = read_gql(sub / 'Kill.gql')
MUTATE_LOAD_EXAMPLE_SCRIPT = read_gql(sub / 'LoadExampleScript.gql')

sub = pwd / 'queries'
QUERY_STATE = read_gql(sub / 'State.gql')
QUERY_RUN_NO = read_gql(sub / 'RunNo.gql')
QUERY_TRACE_IDS = read_gql(sub / 'TraceIds.gql')
QUERY_SOURCE = read_gql(sub / 'Source.gql')
QUERY_SOURCE_LINE = read_gql(sub / 'SourceLine.gql')
QUERY_EXCEPTION = read_gql(sub / 'Exception.gql')
QUERY_CONTINUOUS_ENABLED = read_gql(sub / 'ContinuousEnabled.gql')

sub = pwd / 'subscriptions'
SUBSCRIBE_COUNTER = read_gql(sub / 'Counter.gql')
SUBSCRIBE_STATE = read_gql(sub / 'State.gql')
SUBSCRIBE_RUN_NO = read_gql(sub / 'RunNo.gql')
SUBSCRIBE_TRACE_IDS = read_gql(sub / 'TraceIds.gql')
SUBSCRIBE_PROMPTING = read_gql(sub / 'Prompting.gql')
SUBSCRIBE_STDOUT = read_gql(sub / 'Stdout.gql')
SUBSCRIBE_CONTINUOUS_ENABLED = read_gql(sub / 'ContinuousEnabled.gql')
