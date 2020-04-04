from copy import deepcopy


class Entity(object):
    def __init__(self, id_):
        self._id = id_
        self._version = 0
        self._events = []

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

    def _record(self, evt):
        self._events.append(evt)
