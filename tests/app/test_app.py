from nextlinegraphql import create_app
from nextlinegraphql.factory import create_app_for_test


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
