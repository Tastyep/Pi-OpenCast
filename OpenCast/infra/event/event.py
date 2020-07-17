from dataclasses import dataclass

from OpenCast.infra import Id


@dataclass
class Event:
    id: Id
