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
class PlayerStateUpdated(Event):
    old_state: State
    new_state: State


@dataclass
class PlayerVideoUpdated(Event):
    old_video_id: State
    new_video_id: State


@dataclass
class VideoSeeked(Event):
    duration: int


@dataclass
class VolumeUpdated(Event):
    volume: int


@dataclass
class SubtitleStateUpdated(Event):
    state: bool


@dataclass
class SubtitleDelayUpdated(Event):
    delay: int
