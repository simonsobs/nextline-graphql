import nextline_graphql


def test_version() -> None:
    '''Confirm that the version string is attached to the module'''
    nextline_graphql.__version__
