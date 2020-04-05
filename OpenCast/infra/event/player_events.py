from dataclasses import dataclass

from OpenCast.domain.model.video import Video


@dataclass
class PlayerStarted:
    video: Video


@dataclass
class PlayerStopped:
    interrupted: bool


@dataclass
class PlayerPaused:
    pass


@dataclass
class PlayerUnpaused:
    pass


@dataclass
class SubtitleStateChanged:
    state: bool


@dataclass
class SubtitleDelayUpdated:
    amount: int


@dataclass
class VolumeUpdated:
    volume: int


@dataclass
class VideoSeeked:
    pass
