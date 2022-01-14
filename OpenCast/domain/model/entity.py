""" Abstract representation of a versionable entity """

from copy import deepcopy


class Entity:
    def __init__(self, data_cls, *args, **kwargs):
        if args and type(args[0]) is data_cls:  # Initialized from a dict
            self._data = args[0]
        else:
            self._data = data_cls(*args, **kwargs)
        self._events = []

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.id == other.id

    def __repr__(self):
        return f"{type(self).__name__}({self._data})"

    @classmethod
    def from_dict(cls, data: dict):
        clsdata = cls.Schema().load(data)
        entity = cls(cls.Data(**clsdata))
        entity._events.clear()
        return entity

    @property
    def id(self):
        return self._data.id

    def release_events(self):
        events = deepcopy(self._events)
        self._events.clear()
        return events

    def to_dict(self):
        return self.Schema().dump(self._data)

    def _record(self, evtcls, *args):
        self._events.append({evtcls: (self.id,) + args})
