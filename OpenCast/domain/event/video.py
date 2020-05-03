from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from .event import Event


@dataclass
class VideoCreated(Event):
    source: str
    playlist_id: UUID


@dataclass
class VideoIdentified(Event):
    title: str


@dataclass
class VideoRetrieved(Event):
    path: Path


@dataclass
class VideoSubtitleFetched(Event):
    subtitle: Path
