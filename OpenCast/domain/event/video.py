""" Events emitted by the video model """


from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from OpenCast.domain.model.video import State

from .event import Event, ModelId


@dataclass
class VideoCreated(Event):
    source: str
    collection_id: Optional[ModelId]
    album: Optional[str]
    title: Optional[str]
    duration: Optional[int]
    source_protocol: str
    thumbnail: Optional[str]
    state: State


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
class VideoStateUpdated(Event):
    old: State
    new: State
