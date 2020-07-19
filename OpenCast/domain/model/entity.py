from collections import OrderedDict
from copy import deepcopy

from . import Id


class Entity:
    def __init__(self, id_: Id):
        self._id = id_
        self._version = 0
        self._events = OrderedDict()

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def __repr__(self):
        return f"id: {self.id}, version: {self.version}"

    @property
    def id(self):
        return self._id

    @property
    def version(self):
        return self._version

    def update_version(self):
        self._version += 1

    def release_events(self):
        events = deepcopy(self._events)
        self._events.clear()
        return events

    def to_dict(self):
        data = self.__dict__
        data.pop("_events")
        return data

    def _record(self, evtcls, *args):
        self._events[evtcls] = (self.id,) + args
