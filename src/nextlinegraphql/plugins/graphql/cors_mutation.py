from collections.abc import AsyncIterator, Sequence

from strawberry.exceptions import StrawberryGraphQLError
from strawberry.extensions import SchemaExtension
from strawberry.types.graphql import OperationType


class CORSMutation(SchemaExtension):
    def __init__(self, allow_origins: Sequence[str]):
        self._allow_origins = allow_origins

    async def on_execute(self) -> AsyncIterator[None]:
        if not self._is_origin_allowed():
            raise StrawberryGraphQLError('GraphQL Mutations not allowed')

        yield

    def _is_origin_allowed(self) -> bool:
        if '*' in self._allow_origins:
            return True

        op_type = self.execution_context.operation_type
        if op_type is not OperationType.MUTATION:
            return True

        request = self.execution_context.context.get('request')
        origin = request.headers.get('origin')
        if origin is None:
            #  Same origin or non-browser request
            return True

        if origin in self._allow_origins:
            return True

        return False
