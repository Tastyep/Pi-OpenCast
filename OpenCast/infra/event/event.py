""" Abstract Event definition """

from dataclasses import asdict, dataclass

from OpenCast.infra import Id


@dataclass
class Event:
    id: Id

    def to_dict(self):
        return asdict(self)
