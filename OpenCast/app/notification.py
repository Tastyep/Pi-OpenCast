from dataclasses import asdict, dataclass

from OpenCast.infra import Id


@dataclass
class Notification:
    id: Id
    message: str

    def to_dict(self):
        return asdict(self)
