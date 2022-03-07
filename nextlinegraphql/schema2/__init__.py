from __future__ import annotations

import strawberry
from strawberry.types import Info

from typing import TYPE_CHECKING, AsyncGenerator, List, Optional

if TYPE_CHECKING:
    from nextline import Nextline


def resolve_source(info: Info, file_name: Optional[str] = None) -> List[str]:
    nextline: Nextline = info.context["nextline"]
    return nextline.get_source(file_name)


@strawberry.type
class Query:
    source: List[str] = strawberry.field(resolver=resolve_source)


def subscribe_global_state(info: Info) -> AsyncGenerator[str, None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_state()


def subscribe_run_no(info: Info) -> AsyncGenerator[int, None]:
    nextline: Nextline = info.context["nextline"]
    return nextline.subscribe_run_no()


@strawberry.type
class Subscription:
    global_state: AsyncGenerator[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_global_state
    )
    run_no: AsyncGenerator[str, None] = strawberry.field(
        is_subscription=True, resolver=subscribe_run_no
    )


schema = strawberry.Schema(query=Query, subscription=Subscription)
