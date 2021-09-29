""" Events emitted by the video model """


from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .event import Event, ModelId


@dataclass
class VideoCreated(Event):
    source: str
    collection_id: Optional[ModelId]
    collection_name: Optional[str]
    title: Optional[str]
    duration: Optional[int]
    source_protocol: str
    thumbnail: Optional[str]


@dataclass
class VideoDeleted(Event):
    pass


@dataclass
class VideoRetrieved(Event):
    location: str


@dataclass
class VideoParsed(Event):
    streams: list


@dataclass
class VideoSubtitleFetched(Event):
    subtitle: Path


@dataclass
class VideoStarted(Event):
    timestamp: int


@dataclass
class VideoStopped(Event):
    playing_duration: int
