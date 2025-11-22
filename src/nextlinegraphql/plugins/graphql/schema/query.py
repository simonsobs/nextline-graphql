import json

import strawberry
from dynaconf import Dynaconf
from strawberry.types import Info


def query_settings(info: Info) -> str:
    settings: Dynaconf = info.context['settings']
    return json.dumps(settings.to_dict())


@strawberry.type
class Query:
    settings: str = strawberry.field(resolver=query_settings)
