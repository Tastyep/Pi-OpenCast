from dataclasses import dataclass
from uuid import UUID

from .event import Event


@dataclass
class PlayerStarted(Event):
    video_id: UUID


@dataclass
class VideoQueued(Event):
    video_id: UUID


@dataclass
class PlayerStopped(Event):
    pass


@dataclass
class PlayerPaused(Event):
    pass


@dataclass
class PlayerUnpaused(Event):
    pass


@dataclass
class VideoSeeked(Event):
    pass


@dataclass
class VolumeUpdated(Event):
    volume: int


@dataclass
class SubtitleStateUpdated(Event):
    pass


@dataclass
class SubtitleDelayUpdated(Event):
    pass
