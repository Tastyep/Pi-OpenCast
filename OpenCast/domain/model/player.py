from enum import Enum

from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.event import player as Evt

from .entity import Entity, Id
from .video import Video


class State(Enum):
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3


class Player(Entity):
    VOLUME_STEP = 10
    SUBTITLE_DELAY_STEP = 100
    SHORT_TIME_STEP = 1000
    LONG_TIME_STEP = 30000

    def __init__(self, id_: Id):
        super().__init__(id_)
        self._state = State.STOPPED
        self._queue = []
        self._index = 0
        self._sub_state = True
        self._sub_delay = 0
        self._volume = 70

    def __repr__(self):
        base_repr = super().__repr__()
        return f"{Player.__name__}({base_repr}, state={self._state}, video_idx={self._index} / {len(self._queue)})"

    @property
    def state(self):
        return self._state

    @property
    def video_queue(self):
        return self._queue

    @property
    def subtitle_state(self):
        return self._sub_state

    @property
    def subtitle_delay(self):
        return self._sub_delay

    @property
    def volume(self):
        return self._volume

    @subtitle_state.setter
    def subtitle_state(self, state):
        self._sub_state = state
        self._record(Evt.SubtitleStateUpdated)

    @subtitle_delay.setter
    def subtitle_delay(self, delay):
        self._sub_delay = delay
        self._record(Evt.SubtitleDelayUpdated)

    @volume.setter
    def volume(self, v):
        self._volume = max(min(200, v), 0)
        self._record(Evt.VolumeUpdated, self._volume)

    def play(self, video: Video):
        if video not in self._queue:
            raise DomainError(f"unknown video: {video}")

        self._index = self._queue.index(video)
        self._state = State.PLAYING
        self._record(Evt.PlayerStarted, video.id)

    def stop(self):
        if self._state is State.STOPPED:
            raise DomainError("the player is already stopped")
        self._state = State.STOPPED
        self._sub_delay = 0
        self._record(Evt.PlayerStopped)

    def queue(self, video: Video, with_priority=False):
        idx = len(self._queue)

        # Try to order videos from the same playlist together
        next_videos = self._queue[self._index :]
        for i, q_video in enumerate(reversed(next_videos)):
            if q_video.playlist_id == video.playlist_id:
                idx = self._index + len(next_videos) - i
                break

        self._queue.insert(idx, video)
        self._record(Evt.VideoQueued, video.id)

    def toggle_pause(self):
        if self._state is State.PLAYING:
            self._state = State.PAUSED
        elif self._state is State.PAUSED:
            self._state = State.PLAYING
        else:
            raise DomainError(f"the player is not started")
        self._record(Evt.PlayerStateToggled)

    def next_video(self):
        if self._index + 1 >= len(self._queue):
            if self._queue and config["player.loop_last"] is True:
                return self._queue[self._index]
            return None

        return self._queue[self._index + 1]

    def seek_video(self):
        self._record(Evt.VideoSeeked)
