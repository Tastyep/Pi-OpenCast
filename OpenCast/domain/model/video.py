""" Conceptual representation of a media """

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from marshmallow import Schema, fields

from OpenCast.domain.event import video as Evt

from . import Id
from .entity import Entity


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
    source_protocol = fields.String(allow_none=True)
    title = fields.String(allow_none=True)
    duration = fields.Integer(allow_none=True)
    collection_id = fields.UUID(allow_none=True)
    collection_name = fields.String(allow_none=True)
    thumbnail = fields.String(allow_none=True)
    location = fields.String(allow_none=True)
    streams = fields.Nested(StreamSchema(many=True))
    subtitle = fields.String(allow_none=True)


class Video(Entity):
    Schema = VideoSchema
    METADATA_FIELDS = [
        "collection_name",
        "title",
        "duration",
        "source_protocol",
        "thumbnail",
    ]

    @dataclass
    class Data:
        id: Id
        source: str
        collection_id: Optional[Id] = None
        collection_name: Optional[str] = None
        title: Optional[str] = None
        duration: Optional[int] = None
        source_protocol: Optional[str] = None
        thumbnail: Optional[str] = None
        location: Optional[str] = None
        streams: List[Stream] = field(default_factory=list)
        subtitle: Optional[str] = None

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)
        self._record(
            Evt.VideoCreated,
            self._data.source,
            self._data.collection_id,
            self._data.collection_name,
            self._data.title,
            self._data.duration,
            self._data.source_protocol,
            self._data.thumbnail,
        )

    @property
    def source(self):
        return self._data.source

    @property
    def collection_id(self):
        return self._data.collection_id

    @property
    def collection_name(self):
        return self._data.collection_name

    @property
    def title(self):
        return self._data.title

    @property
    def duration(self):
        return self._data.duration

    @property
    def location(self):
        return self._data.location

    @property
    def streams(self):
        return self._data.streams

    @property
    def subtitle(self):
        return self._data.subtitle

    @location.setter
    def location(self, location: str):
        self._data.location = location
        self._record(Evt.VideoRetrieved, self._data.location)

    @streams.setter
    def streams(self, streams: List[Stream]):
        self._data.streams = streams
        self._record(Evt.VideoParsed, self._data.streams)

    @subtitle.setter
    def subtitle(self, subtitle: str):
        self._data.subtitle = subtitle
        self._record(Evt.VideoSubtitleFetched, self._data.subtitle)

    def streamable(self):
        return self._data.source_protocol in ["m3u8"]

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
