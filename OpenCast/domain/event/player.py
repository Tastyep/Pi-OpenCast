""" Events emitted by the player model """

from dataclasses import dataclass

from OpenCast.domain.model.player import State

from .event import Event, ModelId


@dataclass
class PlayerCreated(Event):
    queue: ModelId
    state: State
    sub_state: bool
    sub_delay: int
    volume: int


@dataclass
class PlayerQueueUpdated(Event):
    queue: ModelId


@dataclass
class PlayerStateUpdated(Event):
    old: State
    new: State
    video_id: ModelId


@dataclass
class VideoSeeked(Event):
    pass


@dataclass
class VolumeUpdated(Event):
    volume: int


@dataclass
class SubtitleStateUpdated(Event):
    state: bool


@dataclass
class SubtitleDelayUpdated(Event):
    delay: int
