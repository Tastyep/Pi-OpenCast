""" Events emitted by the album model """

from dataclasses import dataclass
from typing import List

from OpenCast.domain.event.event import Event, ModelId


@dataclass
class AlbumCreated(Event):
    name: str
    ids: List[ModelId]
    thumbnail: str


@dataclass
class AlbumDeleted(Event):
    ids: List[ModelId]


@dataclass
class AlbumVideosUpdated(Event):
    ids: List[ModelId]
