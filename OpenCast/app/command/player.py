from uuid import UUID

from .command import Command, command


@command
class PlayVideo(Command):
    video_id: UUID


@command
class QueueVideo(Command):
    video_id: UUID


@command
class StopVideo(Command):
    pass


@command
class ToggleVideoState(Command):
    pass


@command
class SeekVideo(Command):
    duration: int


@command
class NextVideo(Command):
    pass


@command
class PrevVideo(Command):
    pass


@command
class ChangeVolume(Command):
    amount: int


@command
class ToggleSubtitle(Command):
    pass


@command
class IncreaseSubtitleDelay(Command):
    amount: int


@command
class DecreaseSubtitleDelay(Command):
    amount: int
