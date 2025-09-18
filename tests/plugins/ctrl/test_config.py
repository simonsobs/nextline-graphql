from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from pytest import MonkeyPatch

from nextline_test_utils.strategies import st_none_or
from nextlinegraphql.factory import create_app_for_test
from nextlinegraphql.plugins.ctrl import Plugin

DEFAULT_TRACE_MODULES = False
DEFAULT_TRACE_THREADS = False


def test_default() -> None:
    app = create_app_for_test()
    hook = app.hook
    config = app.config
    assert config.ctrl.trace_modules is DEFAULT_TRACE_MODULES
    assert config.ctrl.trace_threads is DEFAULT_TRACE_THREADS

    plugin = hook.get_plugin('ctrl')
    assert isinstance(plugin, Plugin)
    assert plugin._trace_modules is DEFAULT_TRACE_MODULES
    assert plugin._trace_threads is DEFAULT_TRACE_THREADS


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(trace_modules=st_none_or(st.booleans()), trace_threads=st_none_or(st.booleans()))
def test_property(
    trace_modules: bool | None, trace_threads: bool | None, monkeypatch: MonkeyPatch
) -> None:
    with monkeypatch.context() as m:
        pass
        if trace_modules is not None:
            m.setenv('NEXTLINE_CTRL__TRACE_MODULES', str(trace_modules).lower())
        if trace_threads is not None:
            m.setenv('NEXTLINE_CTRL__TRACE_THREADS', str(trace_threads).lower())

        app = create_app_for_test()
        hook = app.hook
        config = app.config

        expected_trace_modules = (
            trace_modules if trace_modules is not None else DEFAULT_TRACE_MODULES
        )
        expected_trace_threads = (
            trace_threads if trace_threads is not None else DEFAULT_TRACE_THREADS
        )

        assert config.ctrl.trace_modules is expected_trace_modules
        assert config.ctrl.trace_threads is expected_trace_threads

        plugin = hook.get_plugin('ctrl')
        assert isinstance(plugin, Plugin)
        assert plugin._trace_modules is expected_trace_modules
        assert plugin._trace_threads is expected_trace_threads
