""" Abstract representation of a domain event """

from dataclasses import asdict, dataclass

from OpenCast.domain.model import Id as ModelId
from OpenCast.infra import Id


@dataclass
class Event:
    id: Id
    model_id: ModelId

    def to_dict(self):
        return asdict(self)
