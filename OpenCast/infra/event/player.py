from dataclasses import dataclass

from OpenCast.domain.model.video import Video
from OpenCast.infra.event.event import Event


@dataclass
class PlayerStarted(Event):
    video: Video


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
class SubtitleStateChanged(Event):
    state: bool


@dataclass
class SubtitleDelayUpdated(Event):
    amount: int


@dataclass
class VolumeUpdated(Event):
    volume: int


@dataclass
class VideoSeeked(Event):
    pass
