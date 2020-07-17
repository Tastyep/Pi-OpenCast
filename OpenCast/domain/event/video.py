from dataclasses import dataclass
from pathlib import Path

from .event import Event, ModelId


@dataclass
class VideoCreated(Event):
    source: str
    playlist_id: ModelId


@dataclass
class VideoDeleted(Event):
    pass


@dataclass
class VideoIdentified(Event):
    title: str


@dataclass
class VideoRetrieved(Event):
    path: Path


@dataclass
class VideoParsed(Event):
    streams: list


@dataclass
class VideoSubtitleFetched(Event):
    subtitle: Path
