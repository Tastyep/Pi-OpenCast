from dataclasses import dataclass
from uuid import UUID

from .command import Command


@dataclass
class PlayVideo(Command):
    video_id: UUID


@dataclass
class QueueVideo(Command):
    video_id: UUID


@dataclass
class StopVideo(Command):
    pass


@dataclass
class ToggleVideoState(Command):
    pass


@dataclass
class SeekVideo(Command):
    duration: int


@dataclass
class NextVideo(Command):
    pass


@dataclass
class PrevVideo(Command):
    pass


@dataclass
class ChangeVolume(Command):
    amount: int


@dataclass
class ToggleSubtitle(Command):
    pass


@dataclass
class IncreaseSubtitleDelay(Command):
    pass


@dataclass
class DecreaseSubtitleDelay(Command):
    pass
