""" Events emitted by the video model """


from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .event import Event


@dataclass
class VideoCreated(Event):
    source: str
    title: Optional[str]
    collection_name: Optional[str]
    thumbnail: Optional[str]


@dataclass
class VideoDeleted(Event):
    pass


@dataclass
class VideoRetrieved(Event):
    path: Path


@dataclass
class VideoParsed(Event):
    streams: list


@dataclass
class VideoSubtitleFetched(Event):
    subtitle: Path
