from .command import Command, ModelId, command


@command
class PlayVideo(Command):
    video_id: ModelId


@command
class QueueVideo(Command):
    video_id: ModelId


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
    video_id: ModelId


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
