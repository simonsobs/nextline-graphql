import strawberry
from strawberry.types import Info

from nextlinegraphql.plugins.continuous.types import ContinuousInfo


def query_continuous_enabled(info: Info) -> bool:
    continuous_info: ContinuousInfo = info.context['continuous_info']
    return continuous_info.pubsub_enabled.latest()


@strawberry.type
class QueryContinuous:
    continuous_enabled: bool = strawberry.field(resolver=query_continuous_enabled)


@strawberry.type
class Query:
    @strawberry.field
    def continuous(self, info: Info) -> QueryContinuous:
        return QueryContinuous()
