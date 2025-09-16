from collections.abc import AsyncIterator, Iterable, MutableMapping
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, TypeAlias

import strawberry
from apluggy import PluginManager
from dynaconf import Dynaconf, Validator
from starlette.applications import Starlette
from starlette.types import ASGIApp
from strawberry.schema import BaseSchema
from strawberry.tools import merge_types

from nextlinegraphql.custom.strawberry import GraphQL
from nextlinegraphql.hook import spec

from .schema import Query

if TYPE_CHECKING:
HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = HERE / 'default.toml'

assert DEFAULT_CONFIG_PATH.is_file()

PRELOAD = (str(DEFAULT_CONFIG_PATH),)
SETTINGS = ()
VALIDATORS = (
    # NOTE: Provide default values `['*']` here so that these values will be overridden
    # by the settings file. If the default values were provided in `default.toml`, the
    # lists would be merged instead of overridden.
    Validator('GRAPHQL.MUTATION_ALLOW_ORIGINS', is_type_of=list, default=['*']),
)


class Plugin:
    @spec.hookimpl
    def dynaconf_preload(self) -> Optional[tuple[str, ...]]:
        return PRELOAD

    @spec.hookimpl
    def dynaconf_settings_files(self) -> Optional[tuple[str, ...]]:
        return SETTINGS

    @spec.hookimpl
    def dynaconf_validators(self) -> Optional[tuple[Validator, ...]]:
        return VALIDATORS

    @spec.hookimpl
    def configure(self, settings: Dynaconf, hook: PluginManager) -> None:
        self._settings = settings
        self._app = _create_app(hook=hook)

    @spec.hookimpl
    def schema(self) -> tuple[type, type | None, type | None]:
        return (Query, None, None)

    @spec.hookimpl(tryfirst=True)  # tryfirst so to be the outermost context
    @asynccontextmanager
    async def lifespan(self, app: Starlette) -> AsyncIterator[None]:
        app.mount('/', self._app)
        yield

    @spec.hookimpl
    def update_strawberry_context(self, context: MutableMapping[str, Any]) -> None:
        context['settings'] = self._settings


def _create_app(hook: PluginManager) -> ASGIApp:
    schema = _compose_schema(hook=hook)
    app = _EGraphQL(schema).set_hook(hook)
    return app


TRIO_LIST: TypeAlias = Iterable[tuple[type | None, type | None, type | None]]


def _compose_schema(hook: PluginManager) -> BaseSchema:
    # [(Query, Mutation, Subscription), ...]
    trio_list: TRIO_LIST = hook.hook.schema()

    Query, Mutation, Subscription = _merge_trios(trio_list)

    schema = strawberry.Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
    )

    return schema


def _merge_trios(trio_list: TRIO_LIST) -> tuple[type, type | None, type | None]:
    # [(Query, ...), (Mutation, ...), (Subscription, ...)]
    transposed = list(map(tuple, zip(*trio_list)))
    transposed = [tuple(t for t in l if t) for l in transposed]  # remove None

    q, m, s = transposed
    assert q  # Query is required
    Query = merge_types('Query', q)
    Mutation = m and merge_types('Mutation', m) or None
    Subscription = s and merge_types('Subscription', s) or None

    return Query, Mutation, Subscription


class _EGraphQL(GraphQL):
    '''Extend the strawberry GraphQL app to override the `get_context` method

    This class is implemented in the way described in the strawberry document:
    https://strawberry.rocks/docs/integrations/asgi
    '''

    def set_hook(self, hook: PluginManager) -> '_EGraphQL':
        self._hook = hook
        return self

    async def get_context(
        self, request: 'Request | WebSocket', response: 'Response | WebSocket'
    ) -> Optional[Any]:
        context = {'request': request, 'response': response}
        self._hook.hook.update_strawberry_context(context=context)
        return context
