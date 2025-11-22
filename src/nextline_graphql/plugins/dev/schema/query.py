import json
from typing import cast

import strawberry
from starlette.requests import Request
from strawberry.types import Info


def query_headers(info: Info) -> str:
    request = cast(Request, info.context['request'])
    return json.dumps(dict(request.headers))


@strawberry.type
class QueryDev:
    headers: str = strawberry.field(resolver=query_headers)


@strawberry.type
class Query:
    @strawberry.field
    def dev(self) -> QueryDev:
        return QueryDev()
