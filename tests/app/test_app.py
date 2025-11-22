from nextline_graphql import create_app
from nextline_graphql.factory import create_app_for_test


def test_app() -> None:
    app = create_app(
        enable_external_plugins=False,
        enable_logging_configuration=False,
        print_settings=False,
    )
    assert app.hook is not None
    assert app.config is not None


def test_create_app_for_test() -> None:
    app = create_app_for_test()
    assert app.hook is not None
    assert app.config is not None


class MockPlugin:
    pass


def test_extra_plugins() -> None:
    plugin = MockPlugin()
    app = create_app_for_test(extra_plugins=[plugin])
    assert plugin in app.hook.get_plugins()
