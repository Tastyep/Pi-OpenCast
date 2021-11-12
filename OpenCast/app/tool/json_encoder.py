""" Custom JSON encoder definitions """

from datetime import datetime, timedelta
from enum import Enum
from json import JSONEncoder
from pathlib import PosixPath

from OpenCast.app.notification import Notification
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
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return obj.total_seconds()
        return super().default(obj)


class ModelEncoder(EnhancedJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Entity):
            return obj.to_dict()
        return super().default(obj)


class EventEncoder(EnhancedJSONEncoder):
    def default(self, obj):
        if (
            isinstance(obj, DomainEvent)
            or isinstance(obj, InfraEvent)
            or isinstance(obj, Notification)
        ):
            return obj.to_dict()
        return super().default(obj)
