from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from .event import Event


@dataclass
class VideoCreated(Event):
    source: str
    playlist_id: UUID
    title: str
    path: Path


@dataclass
class VideoDownloaded(Event):
    pass


@dataclass
class VideoSubtitleFetched(Event):
    subtitle: Path
