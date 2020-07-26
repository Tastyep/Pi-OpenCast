from dataclasses import dataclass

from OpenCast.domain.model import Id as ModelId
from OpenCast.infra import Id


@dataclass
class Event:
    id: Id
    model_id: ModelId
