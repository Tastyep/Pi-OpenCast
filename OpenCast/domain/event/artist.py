""" Events emitted by the artist model """

from dataclasses import dataclass
from typing import List, Optional

from OpenCast.domain.event.event import Event, ModelId


@dataclass
class ArtistCreated(Event):
    name: str
    ids: List[ModelId]
    thumbnail: Optional[str]


@dataclass
class ArtistThumbnailUpdated(Event):
    thumbnail: str


@dataclass
class ArtistDeleted(Event):
    ids: List[ModelId]


@dataclass
class ArtistVideosUpdated(Event):
    ids: List[ModelId]
