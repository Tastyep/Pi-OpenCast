""" Events emitted by the album model """

from dataclasses import dataclass
from typing import List, Optional

from OpenCast.domain.event.event import Event, ModelId


@dataclass
class AlbumCreated(Event):
    name: str
    ids: List[ModelId]
    thumbnail: Optional[str]


@dataclass
class AlbumDeleted(Event):
    ids: List[ModelId]


@dataclass
class AlbumVideosUpdated(Event):
    ids: List[ModelId]
