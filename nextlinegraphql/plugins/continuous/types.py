from asyncio import Task
from dataclasses import dataclass, field
from typing import Set

from nextline.utils.pubsub import PubSubItem


@dataclass
class ContinuousInfo:
    pubsub_enabled: PubSubItem[bool] = field(default_factory=PubSubItem)
    tasks: Set[Task] = field(default_factory=set)
