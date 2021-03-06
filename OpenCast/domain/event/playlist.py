""" Events emitted by the video model """


from dataclasses import dataclass
from typing import List

from .event import Event, ModelId


@dataclass
class PlaylistCreated(Event):
    name: str
    ids: List[ModelId]


@dataclass
class PlaylistDeleted(Event):
    pass


@dataclass
class PlaylistRenamed(Event):
    name: str


@dataclass
class PlaylistContentUpdated(Event):
    ids: List[ModelId]
