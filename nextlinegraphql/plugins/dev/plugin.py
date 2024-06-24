from apluggy import PluginManager
from dynaconf import Dynaconf

from nextlinegraphql.hook import spec

from .schema import Query


class Plugin:
    @spec.hookimpl
    def configure(self, settings: Dynaconf, hook: PluginManager) -> None:
        self._settings = settings

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, None, None)
