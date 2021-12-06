""" Conceptual representation of an album """

from dataclasses import dataclass, field
from typing import List, Optional

from marshmallow import Schema, fields

from OpenCast.domain.error import DomainError
from OpenCast.domain.event import album as Evt
from OpenCast.domain.model import Id
from OpenCast.domain.model.entity import Entity


class AlbumSchema(Schema):
    id = fields.UUID()
    name = fields.String()
    ids = fields.List(fields.UUID())
    thumbnail = fields.String(allow_none=True)


class Album(Entity):
    Schema = AlbumSchema

    @dataclass
    class Data:
        id: Id
        name: str
        ids: List[Id] = field(default_factory=list)
        thumbnail: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(self.Data, *args, **kwargs)
        self._record(
            Evt.AlbumCreated, self._data.name, self._data.ids, self._data.thumbnail
        )

    @property
    def name(self):
        return self._data.name

    @property
    def ids(self):
        return self._data.ids

    def add(self, video_id):
        if video_id in self.ids:
            raise DomainError(
                "video already in album", name=self.name, video_id=video_id
            )
        self._data.ids.append(video_id)
        self._record(Evt.AlbumVideosUpdated, self._data.ids)

    def remove(self, video_id):
        if video_id not in self.ids:
            raise DomainError("video not in album", name=self.name, video_id=video_id)
        self._data.ids.remove(video_id)
        self._record(Evt.AlbumVideosUpdated, self._data.ids)

    def delete(self):
        self._record(Evt.AlbumDeleted, self._data.ids)
