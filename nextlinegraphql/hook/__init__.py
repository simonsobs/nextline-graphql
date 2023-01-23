__all__ = ['spec', 'load_plugins']

from nextlinegraphql.custom.pluggy import PluginManager
from nextlinegraphql.plugins import ctrl, db, graphql

from . import spec


def load_plugins() -> PluginManager:
    '''Return a pluggy PluginManager with the plugins registered'''

    pm = PluginManager(spec.PROJECT_NAME)
    pm.add_hookspecs(spec)

    # The hooks are called in the reverse order of the plugin registration.
    # https://pluggy.readthedocs.io/en/stable/#call-time-order
    pm.register(graphql.Plugin())
    pm.register(ctrl.Plugin())
    pm.load_setuptools_entrypoints(spec.PROJECT_NAME)
    pm.register(db.Plugin())

    return pm
