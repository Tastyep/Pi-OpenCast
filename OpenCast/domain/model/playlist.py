""" Conceptual representation of a playlist """

from dataclasses import dataclass, field
from typing import List

from marshmallow import Schema, fields

from OpenCast.domain.event import playlist as Evt

from . import Id
from .entity import Entity


class PlaylistSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    ids = fields.List(fields.UUID())


class Playlist(Entity):
    Schema = PlaylistSchema

    @dataclass
    class Data:
        id: Id
        name: str
        ids: List[Id] = field(default_factory=list)

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)
        self._record(Evt.PlaylistCreated, self._data.name, self._data.ids)

    @property
    def name(self):
        return self._data.name

    @property
    def ids(self):
        return self._data.ids

    @name.setter
    def name(self, value: str):
        self._data.name = value
        self._record(Evt.PlaylistRenamed, self._data.name)

    @ids.setter
    def ids(self, value: List[Id]):
        self._data.ids = value
        self._record(Evt.PlaylistContentUpdated, self._data.ids)

    def delete(self):
        self._record(Evt.PlaylistDeleted)
