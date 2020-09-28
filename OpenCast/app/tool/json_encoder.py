""" Custom JSON encoder definitions """

import dataclasses
from enum import Enum
from json import JSONEncoder
from pathlib import Path

from OpenCast.domain.event.event import Event
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
        return data


class EventEncoder(EnhancedJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return self._encode_event(obj)
        return super().default(obj)

    def _encode_event(self, obj):
        data = obj.to_dict()
        return data
