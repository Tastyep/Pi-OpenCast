""" Events emitted by the player model """

from dataclasses import dataclass

from OpenCast.domain.model.player import State

from .event import Event, ModelId


@dataclass
class PlayerCreated(Event):
    state: State
    sub_state: bool
    sub_delay: int
    volume: int


@dataclass
class PlayerStarted(Event):
    video_id: ModelId


@dataclass
class VideoQueued(Event):
    video_id: ModelId


@dataclass
class VideoRemoved(Event):
    video_id: ModelId


@dataclass
class PlayerStopped(Event):
    pass


@dataclass
class PlayerStateToggled(Event):
    state: State


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
