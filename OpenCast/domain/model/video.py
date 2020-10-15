""" Conceptual representation of a media """

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from marshmallow import Schema, fields

from OpenCast.domain.event import video as Evt

from . import Id
from .entity import Entity
from .fields import PathField


@dataclass
class Stream:
    index: int
    type: str
    language: Optional[str]


class StreamSchema(Schema):
    index = fields.Integer()
    type = fields.String()
    language = fields.String(allow_none=True)


class VideoSchema(Schema):
    id = fields.UUID()
    source = fields.String()
    title = fields.String(allow_none=True)
    collection_name = fields.String(allow_none=True)
    thumbnail = fields.String(allow_none=True)
    path = PathField(allow_none=True)
    streams = fields.Nested(StreamSchema(many=True))
    subtitle = fields.String(allow_none=True)


class Video(Entity):
    Schema = VideoSchema
    METADATA_FIELDS = ["title", "collection_name", "thumbnail"]

    @dataclass
    class Data:
        id: Id
        source: str
        title: Optional[str] = None
        collection_name: Optional[str] = None
        thumbnail: Optional[str] = None
        path: Optional[Path] = None
        streams: List[Stream] = field(default_factory=list)
        subtitle: Optional[str] = None

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)
        self._record(
            Evt.VideoCreated,
            self._data.source,
            self._data.title,
            self._data.collection_name,
            self._data.thumbnail,
        )

    @property
    def source(self):
        return self._data.source

    @property
    def path(self):
        return self._data.path

    @property
    def title(self):
        return self._data.title

    @property
    def collection_name(self):
        return self._data.collection_name

    @property
    def streams(self):
        return self._data.streams

    @property
    def subtitle(self):
        return self._data.subtitle

    @path.setter
    def path(self, path: Path):
        self._data.path = path
        self._record(Evt.VideoRetrieved, self._data.path)

    @streams.setter
    def streams(self, streams: List[Stream]):
        self._data.streams = streams
        self._record(Evt.VideoParsed, self._data.streams)

    @subtitle.setter
    def subtitle(self, subtitle: str):
        self._data.subtitle = subtitle
        self._record(Evt.VideoSubtitleFetched, self._data.subtitle)

    def from_disk(self):
        return Path(self._data.source).is_file()

    def stream(self, type: str, language: str):
        return next(
            (
                stream
                for stream in self._data.streams
                if stream.type == type and stream.language == language
            ),
            None,
        )

    def delete(self):
        self._record(Evt.VideoDeleted)
