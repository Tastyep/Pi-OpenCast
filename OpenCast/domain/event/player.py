from dataclasses import dataclass

from .event import Event, ModelId


@dataclass
class PlayerStarted(Event):
    video_id: ModelId


@dataclass
class VideoQueued(Event):
    video_id: ModelId


@dataclass
class PlayerStopped(Event):
    pass


@dataclass
class PlayerStateToggled(Event):
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
