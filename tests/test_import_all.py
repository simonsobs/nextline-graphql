from nextline_graphql import *  # noqa: F403, F401


def test_import_all() -> None:
    assert 'create_app' in globals()
