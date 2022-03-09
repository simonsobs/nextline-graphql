from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd.joinpath("mutations")
MUTATE_EXEC = sub.joinpath("Exec.gql").read_text()
MUTATE_RESET = sub.joinpath("Reset.gql").read_text()
MUTATE_SEND_PDB_COMMAND = sub.joinpath("SendPdbCommand.gql").read_text()

sub = pwd.joinpath("queries")
QUERY_STATE = sub.joinpath("State.gql").read_text()
QUERY_EXCEPTION = sub.joinpath("Exception.gql").read_text()
QUERY_RUNS = sub.joinpath("Runs.gql").read_text()
QUERY_SOURCE = sub.joinpath("Source.gql").read_text()
QUERY_SOURCE_LINE = sub.joinpath("SourceLine.gql").read_text()

sub = pwd.joinpath("subscriptions")
SUBSCRIBE_COUNTER = sub.joinpath("Counter.gql").read_text()
SUBSCRIBE_STATE = sub.joinpath("State.gql").read_text()
SUBSCRIBE_STDOUT = sub.joinpath("Stdout.gql").read_text()
SUBSCRIBE_TRACE_IDS = sub.joinpath("TraceIds.gql").read_text()
SUBSCRIBE_PROMPTING = sub.joinpath("Prompting.gql").read_text()
