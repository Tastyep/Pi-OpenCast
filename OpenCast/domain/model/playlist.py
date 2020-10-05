""" Conceptual representation of a playlist """

from dataclasses import dataclass
from typing import List

from marshmallow import Schema, fields, post_load

from OpenCast.domain.event import playlist as Evt

from . import Id
from .entity import Entity


class PlaylistSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    ids = fields.List(fields.UUID())

    @post_load
    def make_playlist(self, data, **_):
        playlist = Playlist(**data)
        playlist._events.clear()
        return playlist


class Playlist(Entity):
    Schema = PlaylistSchema

    @dataclass
    class Data:
        id: Id
        name: str
        ids: List[Id]

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
