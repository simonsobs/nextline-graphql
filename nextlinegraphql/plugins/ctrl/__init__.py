__all__ = ['Plugin']

from nextlinegraphql import spec

from .schema import Mutation, Query, Subscription


class Plugin:
    @spec.hookimpl
    def schema(self):
        return (Query, Mutation, Subscription)
