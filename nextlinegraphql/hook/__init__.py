__all__ = ['spec', 'load_plugins']

from apluggy import PluginManager

from nextlinegraphql.plugins import ctrl, dev, graphql

from . import spec


def load_plugins(
    external: bool = True, plugins: list[object] | None = None
) -> PluginManager:
    '''Return a pluggy PluginManager with the plugins registered'''

    pm = PluginManager(spec.PROJECT_NAME)
    pm.add_hookspecs(spec)

    # The hooks are called in the reverse order of the plugin registration.
    # https://pluggy.readthedocs.io/en/stable/#call-time-order
    pm.register(graphql.Plugin(), name='graphql')
    pm.register(ctrl.Plugin(), name='ctrl')
    pm.register(dev.Plugin(), name='dev')
    # pm.set_blocked('schedule')

    if external:
        pm.load_setuptools_entrypoints(spec.PROJECT_NAME)

    if plugins:
        for plugin in plugins:
            pm.register(plugin)

    return pm
