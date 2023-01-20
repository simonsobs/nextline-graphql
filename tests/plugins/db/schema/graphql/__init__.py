from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd / 'queries'
QUERY_HISTORY = (sub / 'History.gql').read_text()
QUERY_HISTORY_RUNS = (sub / 'HistoryRuns.gql').read_text()

# sub = pwd / 'mutations'

# sub = pwd / 'subscriptions'
