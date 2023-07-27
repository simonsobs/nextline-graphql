from typing import AsyncIterator

import strawberry
from strawberry.types import Info

from nextlinegraphql.plugins.continuous.types import ContinuousInfo


def subscribe_continuous_enabled(info: Info) -> AsyncIterator[bool]:
    continuous_info: ContinuousInfo = info.context['continuous_info']
    return continuous_info.pubsub_enabled.subscribe()


@strawberry.type
class Subscription:
    continuous_enabled: AsyncIterator[bool] = strawberry.field(
        is_subscription=True, resolver=subscribe_continuous_enabled
    )
