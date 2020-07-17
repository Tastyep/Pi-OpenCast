from uuid import UUID

from .command import Command, command


@command
class PlayVideo(Command):
    video_id: UUID


@command
class QueueVideo(Command):
    video_id: UUID


@command
class StopPlayer(Command):
    pass


@command
class ToggleVideoState(Command):
    pass


@command
class SeekVideo(Command):
    duration: int


@command
class PickVideo(Command):
    video_id: UUID


@command
class ChangeVolume(Command):
    volume: int


@command
class ToggleSubtitle(Command):
    pass


@command
class IncreaseSubtitleDelay(Command):
    amount: int


@command
class DecreaseSubtitleDelay(Command):
    amount: int
