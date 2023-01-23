__all__ = ['spec', 'initialize_plugins']

from nextlinegraphql.custom.pluggy import PluginManager
from nextlinegraphql.plugins import ctrl, db

from . import spec


def initialize_plugins() -> PluginManager:
    '''Return a pluggy PluginManager with the plugins registered'''
    pm = PluginManager(spec.PROJECT_NAME)
    pm.add_hookspecs(spec)
    pm.load_setuptools_entrypoints(spec.PROJECT_NAME)
    pm.register(db.Plugin())
    pm.register(ctrl.Plugin())
    return pm
