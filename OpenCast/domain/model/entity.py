from collections import OrderedDict
from copy import deepcopy


class Entity:
    def __init__(self, id_):
        self._id = id_
        self._version = 0
        self._events = OrderedDict()

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

    def _record(self, evtcls, *args):
        self._events[evtcls] = (self.id,) + args
