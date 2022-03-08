from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd.joinpath("mutations")
MUTATE_EXEC = sub.joinpath("exec.gql").read_text()
MUTATE_RESET = sub.joinpath("reset.gql").read_text()
MUTATE_SEND_PDB_COMMAND = sub.joinpath("SendPdbCommand.gql").read_text()

sub = pwd.joinpath("queries")
QUERY_EXCEPTION = sub.joinpath("exception.gql").read_text()
QUERY_RUNS = sub.joinpath("runs.gql").read_text()
QUERY_SOURCE = sub.joinpath("source.gql").read_text()

sub = pwd.joinpath("subscriptions")
SUBSCRIBE_COUNTER = sub.joinpath("counter.gql").read_text()
SUBSCRIBE_GLOBAL_STATE = sub.joinpath("GlobalState.gql").read_text()
SUBSCRIBE_STDOUT = sub.joinpath("stdout.gql").read_text()
SUBSCRIBE_TRACE_IDS = sub.joinpath("TraceIds.gql").read_text()
SUBSCRIBE_TRACE_STATE = sub.joinpath("TraceState.gql").read_text()
