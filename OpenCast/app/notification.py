from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from typing import Optional

from OpenCast.infra import Id


class Level(Enum):
    INFO = auto()
    ERROR = auto()


@dataclass
class NotificationBase:
    id: Optional[Id]

    def to_dict(self):
        return asdict(self)


@dataclass
class Notification(NotificationBase):
    level: Level
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class WSResponse(NotificationBase):
    code: str
    content: dict
