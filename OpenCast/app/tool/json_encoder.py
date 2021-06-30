""" Custom JSON encoder definitions """

from json import JSONEncoder
from pathlib import PosixPath
from enum import Enum

from OpenCast.domain.event.event import Event
from OpenCast.domain.model.entity import Entity
from OpenCast.infra import Id


class EnhancedJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Id) or isinstance(obj, PosixPath):
            return str(obj)
        if isinstance(obj, Enum):
            return obj.name
        return super().default(obj)


class ModelEncoder(EnhancedJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Entity):
            return obj.to_dict()
        return super().default(obj)


class EventEncoder(EnhancedJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Event):
            return obj.to_dict()
        return super().default(obj)
