from nextlinegraphql import create_app


def test_app() -> None:
    app = create_app(
        enable_external_plugins=False,
        enable_logging_configuration=False,
        print_settings=False,
    )
    assert app.hook is not None
    assert app.config is not None
