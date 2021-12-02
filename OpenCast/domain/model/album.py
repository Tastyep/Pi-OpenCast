from dataclasses import dataclass
from typing import List, Optional

from marshmallow import Schema, fields

from OpenCast.domain.event import album as Evt
from OpenCast.domain.model import Id
from OpenCast.domain.model.entity import Entity


class AlbumSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    ids = fields.List(fields.UUID())
    thumbnail = fields.String()


class Album(Entity):
    @dataclass
    class Data:
        id: Id
        name: str
        ids: List[Id]
        thumbnail: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(self.Data, *args, **kwargs)
        self._record(
            Evt.AlbumCreated, self._data.name, self._data.thumbnail, self._data.ids
        )

    @property
    def ids(self):
        return self._data.ids

    @ids.setter
    def ids(self, ids: List[Id]):
        self._data.ids = ids

    def delete(self):
        self._record(Evt.AlbumDeleted, self._data.ids)
