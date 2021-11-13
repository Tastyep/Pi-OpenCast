from dataclasses import asdict, dataclass
from enum import Enum, auto

from OpenCast.infra import Id


class Level(Enum):
    INFO = auto()
    ERROR = auto()


@dataclass
class Notification:
    id: Id
    level: Level
    message: str

    def to_dict(self):
        return asdict(self)
