""" Conceptual representation of a media """

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from marshmallow import Schema, fields, post_load

from OpenCast.domain.event import video as Evt

from . import Id
from .entity import Entity
from .fields import PathField


@dataclass
class Stream:
    index: int
    type: str
    language: str


class StreamSchema(Schema):
    index = fields.Integer()
    type = fields.String()
    language = fields.String()


class VideoSchema(Schema):
    id = fields.UUID()
    source = fields.String()
    playlist_id = fields.UUID(allow_none=True)
    thumbnail = fields.String(allow_none=True)
    title = fields.String(allow_none=True)
    path = PathField(allow_none=True)
    streams = fields.Nested(StreamSchema(many=True))
    subtitle = fields.String(allow_none=True)

    @post_load
    def make_video(self, data, **_):
        print(f"GENERATED: {data}")
        return Video(**data)


class Video(Entity):
    Schema = VideoSchema
    METADATA_FIELDS = ["title", "thumbnail"]

    @dataclass
    class Data:
        id: Id
        source: str
        playlist_id: Optional[Id] = None
        thumbnail: Optional[str] = None
        title: Optional[str] = None
        path: Optional[Path] = None
        streams: List[Stream] = field(default_factory=list)
        subtitle: Optional[str] = None

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)
        self._record(Evt.VideoCreated, self._data.source, self._data.playlist_id)

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
    def playlist_id(self):
        return self._data.playlist_id

    @property
    def streams(self):
        return self._data.streams

    @property
    def subtitle(self):
        return self._data.subtitle

    def metadata(self, metadata: dict):
        self._data.title = metadata.get("title", None)
        self._data.thumbnail = metadata.get("thumbnail", None)
        self._record(Evt.VideoIdentified, metadata)

    metadata = property(None, metadata)

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
