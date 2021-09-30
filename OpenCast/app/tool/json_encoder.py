""" Custom JSON encoder definitions """

from enum import Enum
from json import JSONEncoder
from pathlib import PosixPath

from OpenCast.domain.event.event import Event as DomainEvent
from OpenCast.domain.model.entity import Entity
from OpenCast.infra import Id
from OpenCast.infra.event.event import Event as InfraEvent


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
        if isinstance(obj, DomainEvent) or isinstance(obj, InfraEvent):
            return obj.to_dict()
        return super().default(obj)
