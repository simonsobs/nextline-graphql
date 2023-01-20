__all__ = ['Query', 'Mutation', 'Subscription']
import strawberry

from .query import Query


@strawberry.type
class Mutation:
    pass


@strawberry.type
class Subscription:
    pass
