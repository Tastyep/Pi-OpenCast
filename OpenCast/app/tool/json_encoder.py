import dataclasses
from enum import Enum
from json import JSONEncoder
from pathlib import Path

from OpenCast.domain.model.entity import Entity
from OpenCast.infra import Id


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, Id):
            return obj.hex
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.name
        return super().default(obj)


class ModelEncoder(EnhancedJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Entity):
            return self._encode_entity(obj)
        return super().default(obj)

    def _encode_entity(self, obj):
        data = obj.to_dict()
        data = {k[1:] if k[0] == "_" else k: v for k, v in data.items()}
        data.pop("version")
        return data
