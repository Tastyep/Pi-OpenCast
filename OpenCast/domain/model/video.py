""" Conceptual representation of a media """

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from re import compile as reg_compile
from re import search as reg_search
from typing import Callable, Generic, List, Optional, TypeVar

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from OpenCast.domain.error import DomainError
from OpenCast.domain.event import video as Evt

from . import Id
from .entity import Entity


class State(Enum):
    CREATED = 1
    COLLECTING = 2
    READY = 3
    PAUSED = 4
    PLAYING = 5


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
    duration = fields.TimeDelta(allow_none=True)
    total_playing_duration = fields.TimeDelta()
    last_play = fields.DateTime(allow_none=True)
    collection_id = fields.UUID(allow_none=True)
    artist_id = fields.UUID(allow_none=True)
    album_id = fields.UUID(allow_none=True)
    thumbnail = fields.String(allow_none=True)
    location = fields.String(allow_none=True)
    streams = fields.Nested(StreamSchema(many=True))
    subtitle = fields.String(allow_none=True)
    state = EnumField(State)


T = TypeVar("T")


@dataclass
class Metadata(Generic[T]):
    name: str
    post_processor: Optional[Callable[[T, dict], T]] = None


def title_processor():
    def impl(title: str, metadata: dict):
        artist = metadata["artist"]
        if artist is None:
            return title

        match = reg_search(f"^{artist}.* - ", title)
        if not match:
            return title

        return title[match.end() :]

    return impl


def artist_processor():
    pattern = reg_compile(r"[,]")

    def impl(artist: str, _):
        return pattern.split(artist)[0]

    return impl


METADATA_FIELDS = [
    Metadata[str]("artist", artist_processor()),
    Metadata[str]("album"),
    Metadata[str]("title", title_processor()),
    Metadata[int]("duration"),
    Metadata[str]("source_protocol"),
    Metadata[str]("thumbnail"),
]


class Video(Entity):
    Schema = VideoSchema

    @dataclass
    class Data:
        id: Id
        source: str
        collection_id: Optional[Id] = None
        artist_id: Optional[Id] = None
        album_id: Optional[Id] = None
        title: Optional[str] = None
        duration: Optional[timedelta] = None
        total_playing_duration: timedelta = timedelta()
        last_play: Optional[datetime] = None
        source_protocol: Optional[str] = None
        thumbnail: Optional[str] = None
        location: Optional[str] = None
        streams: List[Stream] = field(default_factory=list)
        subtitle: Optional[str] = None
        state: State = State.CREATED

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)
        self._record(
            Evt.VideoCreated,
            self._data.source,
            self._data.collection_id,
            self._data.artist_id,
            self._data.album_id,
            self._data.title,
            self.duration,
            self._data.source_protocol,
            self._data.thumbnail,
            self._data.state,
        )

    @property
    def source(self):
        return self._data.source

    @property
    def collection_id(self):
        return self._data.collection_id

    @property
    def artist_id(self):
        return self._data.artist_id

    @property
    def album_id(self):
        return self._data.album_id

    @property
    def title(self):
        return self._data.title

    @property
    def duration(self):
        return (
            self._data.duration.total_seconds()
            if self._data.duration is not None
            else None
        )

    @property
    def location(self):
        return self._data.location

    @property
    def streams(self):
        return self._data.streams

    @property
    def subtitle(self):
        return self._data.subtitle

    @property
    def state(self):
        return self._data.state

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

    @state.setter
    def state(self, state: State):
        if state == self._data.state:
            return

        old = self._data.state
        self._data.state = state
        self._record(
            Evt.VideoStateUpdated,
            old,
            self._data.state,
            self._data.total_playing_duration,
            self._data.last_play,
        )

    def streamable(self):
        return self._data.source_protocol in ["m3u8", "m3u8_native"]

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

    def start(self):
        if self.state is State.PLAYING:
            raise DomainError("the video is already started", title=self.title)
        if self.state not in [State.READY, State.PAUSED]:
            raise DomainError(
                "the video is not ready", title=self.title, state=self.state
            )
        self._data.last_play = datetime.now()
        self.state = State.PLAYING

    def pause(self):
        if self.state not in [State.PLAYING, State.PAUSED]:
            raise DomainError(
                "the video is not started", title=self.title, state=self.state
            )
        if self.state is State.PAUSED:
            self.start()
        else:
            self._data.total_playing_duration += datetime.now() - self._data.last_play
            self.state = State.PAUSED

    def stop(self):
        if self.state is not State.PLAYING:
            raise DomainError(
                "the video is not started", title=self.title, state=self.state
            )
        self._data.total_playing_duration += datetime.now() - self._data.last_play
        self.state = State.READY

    def delete(self):
        self._record(Evt.VideoDeleted)
