from typing import Any, Optional

import strawberry
from nextline import Nextline
from strawberry.schema import BaseSchema
from strawberry.tools import merge_types

from .custom.pluggy import PluginManager
from .custom.strawberry import GraphQL


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

    def __init__(
        self,
        schema: BaseSchema,
        nextline: Nextline,
        hook: PluginManager,
    ):
        super().__init__(schema)
        self._nextline = nextline
        self._hook = hook

    async def get_context(self, request, response=None) -> Optional[Any]:
        context = {
            "request": request,
            "response": response,
            "nextline": self._nextline,
        }
        updates = await self._hook.ahook.get_context(context=context)
        for update in updates:
            if update:
                context.update(update)
        return context
