from hypothesis import HealthCheck, given, settings
from pytest import MonkeyPatch

from nextline_graphql.factory import create_app_for_test
from nextline_graphql.plugins.graphql import Plugin
from nextline_test_utils.strategies import st_none_or
from tests.app.cors.strategies import st_allow_origins


def test_default() -> None:
    app = create_app_for_test()
    hook = app.hook
    config = app.config
    assert config.graphql.mutation_allow_origins == ['*']

    plugin = hook.get_plugin('graphql')
    assert isinstance(plugin, Plugin)
    assert plugin._settings is config


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(allow_origins=st_none_or(st_allow_origins()))
def test_property(allow_origins: list[str] | None, monkeypatch: MonkeyPatch) -> None:
    with monkeypatch.context() as m:
        if allow_origins is not None:
            m.setenv('NEXTLINE_GRAPHQL__MUTATION_ALLOW_ORIGINS', repr(allow_origins))

        app = create_app_for_test()
        config = app.config

        expected = allow_origins if allow_origins is not None else ['*']
        assert config.graphql.mutation_allow_origins == expected