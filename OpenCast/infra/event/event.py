""" Abstract Event definition """

from dataclasses import asdict, dataclass
from typing import Optional

from OpenCast.infra import Id


@dataclass
class Event:
    id: Optional[Id]

    def to_dict(self):
        return asdict(self)
