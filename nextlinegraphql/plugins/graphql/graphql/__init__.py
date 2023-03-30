from pathlib import Path

pwd = Path(__file__).resolve().parent

sub = pwd / 'queries'
QUERY_SETTINGS = (sub / 'Settings.gql').read_text()
