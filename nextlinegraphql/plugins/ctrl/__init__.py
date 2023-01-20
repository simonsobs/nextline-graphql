__all__ = ['Plugin']
from dynaconf import Dynaconf

from nextlinegraphql import spec

from .schema import Mutation, Query, Subscription


class Plugin:
    @spec.hookimpl
    def configure(self, settings: Dynaconf):
        del settings

    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)
