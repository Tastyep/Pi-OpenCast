""" Player commands """

from .command import Command, ModelId, command


@command
class PlayVideo(Command):
    video_id: ModelId


@command
class QueueVideo(Command):
    video_id: ModelId


@command
class RemoveVideo(Command):
    video_id: ModelId


@command
class StopPlayer(Command):
    pass


@command
class TogglePlayerState(Command):
    pass


@command
class SeekVideo(Command):
    duration: int


@command
class UpdateVolume(Command):
    volume: int


@command
class ToggleSubtitle(Command):
    pass


@command
class AdjustSubtitleDelay(Command):
    amount: int


@command
class DecreaseSubtitleDelay(Command):
    amount: int
