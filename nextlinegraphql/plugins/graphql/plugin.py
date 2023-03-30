from typing import Any, MutableMapping, Optional

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
        self._app = create_app(hook=hook)

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


def create_app(hook: PluginManager) -> ASGIApp:

    schema = compose_schema(hook=hook)

    app = EGraphQL(schema=schema, hook=hook)

    return app


def compose_schema(hook: PluginManager) -> BaseSchema:

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


class EGraphQL(GraphQL):
    """Extend the strawberry GraphQL app

    https://strawberry.rocks/docs/integrations/asgi
    """

    def __init__(self, schema: BaseSchema, hook: PluginManager):
        super().__init__(schema)
        self._hook = hook

    async def get_context(self, request, response=None) -> Optional[Any]:
        context = {'request': request, 'response': response}
        self._hook.hook.update_strawberry_context(context=context)
        return context
