__all__ = ['Plugin']
from dynaconf import Dynaconf

from nextlinegraphql import spec

from .schema import Mutation, Query, Subscription


class Plugin:
    def __init__(self, config: Dynaconf):
        pass

    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)
