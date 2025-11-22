from pathlib import Path

from graphql import parse, print_ast


def read_gql(path: Path | str) -> str:
    '''Load a GraphQL query from a file while checking its syntax.'''

    text = Path(path).read_text()
    parsed = parse(text)
    reformatted = print_ast(parsed)
    return reformatted


pwd = Path(__file__).resolve().parent


sub = pwd / 'queries'
QUERY_HEADERS = read_gql(sub / 'Headers.gql')
