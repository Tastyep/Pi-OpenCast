from dataclasses import dataclass


@dataclass
class PlayerStarted:
    pass


@dataclass
class VideoQueued:
    pass


@dataclass
class PlayerStopped:
    pass


@dataclass
class PlayerPause:
    pass


@dataclass
class PlayerUnpaused:
    pass


@dataclass
class VideoNexted:
    pass


@dataclass
class VideoPreved:
    pass


@dataclass
class VideoSeeked:
    pass


@dataclass
class VolumeUpdated:
    pass


@dataclass
class SubtitleStateUpdated:
    pass


@dataclass
class SubtitleDelayUpdated:
    pass
