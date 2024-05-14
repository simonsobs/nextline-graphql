from nextlinegraphql import *  # noqa: F403, F401


def test_import_all():
    assert 'create_app' in globals()
