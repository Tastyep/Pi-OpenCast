from dataclasses import dataclass

from OpenCast.domain.model.video import Video


@dataclass
class PlayerStarted(object):
    video: Video


@dataclass
class PlayerStopped(object):
    interrupted: bool


@dataclass
class PlayerPaused(object):
    pass


@dataclass
class PlayerUnpaused(object):
    pass


@dataclass
class SubtitleStateChanged(object):
    state: bool


@dataclass
class SubtitleDelayUpdated(object):
    amount: int


@dataclass
class VolumeUpdated(object):
    volume: int


@dataclass
class VideoSeeked(object):
    pass
