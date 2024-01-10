from collections.abc import MutableMapping
from typing import Any, Optional

import strawberry
from apluggy import PluginManager, asynccontextmanager
from dynaconf import Dynaconf
from starlette.applications import Starlette
from starlette.types import ASGIApp
from strawberry.schema import BaseSchema
from strawberry.tools import merge_types

from nextlinegraphql.custom.strawberry import GraphQL
from nextlinegraphql.hook import spec

from .schema import Query


class Plugin:
    @spec.hookimpl
    def configure(self, settings: Dynaconf, hook: PluginManager) -> None:
        self._settings = settings
        self._app = _create_app(hook=hook)

    @spec.hookimpl
    def schema(self):
        return (Query, None, None)

    @spec.hookimpl(tryfirst=True)  # tryfirst so to be the outermost context
    @asynccontextmanager
    async def lifespan(self, app: Starlette):
        app.mount('/', self._app)
        yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping[str, Any]) -> None:
        context['settings'] = self._settings


def _create_app(hook: PluginManager) -> ASGIApp:
    schema = _compose_schema(hook=hook)
    app = _EGraphQL(schema).set_hook(hook)
    return app


def _compose_schema(hook: PluginManager) -> BaseSchema:
    # [(Query, Mutation, Subscription), ...]
    three_types = hook.hook.schema()

    # [(Query, ...), (Mutation, ...), (Subscription, ...)]
    transposed = list(map(tuple, zip(*three_types)))
    transposed = [tuple(t for t in l if t) for l in transposed]  # remove None

    q, m, s = transposed
    assert q  # Query is required
    Query = merge_types('Query', q)  # type: ignore
    Mutation = m and merge_types('Mutation', m) or None  # type: ignore
    Subscription = s and merge_types('Subscription', s) or None  # type: ignore

    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
    )

    return schema


class _EGraphQL(GraphQL):
    '''Extend the strawberry GraphQL app to override the `get_context` method

    This class is implemented in the way described in the strawberry document:
    https://strawberry.rocks/docs/integrations/asgi
    '''

    def set_hook(self, hook: PluginManager) -> '_EGraphQL':
        self._hook = hook
        return self

    async def get_context(self, request, response=None) -> Optional[Any]:
        context = {'request': request, 'response': response}
        self._hook.hook.update_strawberry_context(context=context)
        return context
