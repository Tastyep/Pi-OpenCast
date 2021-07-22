""" Player commands """

from .command import Command, ModelId, command


@command
class CreatePlayer(Command):
    playlist_id: ModelId


@command
class PlayVideo(Command):
    video_id: ModelId
    playlist_id: ModelId


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
