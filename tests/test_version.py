import nextlinegraphql


def test_version() -> None:
    '''Confirm that the version string is attached to the module'''
    nextlinegraphql.__version__
