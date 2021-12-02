""" Events emitted by the album model """

from dataclasses import dataclass
from typing import List

from OpenCast.domain.event.event import Event, ModelId


@dataclass
class AlbumCreated(Event):
    name: str
    thumbnail: str
    ids: List[ModelId]


@dataclass
class AlbumDeleted(Event):
    ids: List[ModelId]


@dataclass
class AlbumVideosUpdated:
    ids: List[ModelId]
