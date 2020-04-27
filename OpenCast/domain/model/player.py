from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.event import player as Evt

from .entity import Entity
from .player_state import PlayerState


class Player(Entity):
    def __init__(self, id_):
        super(Player, self).__init__(id_)
        self._state = PlayerState.STOPPED
        self._queue = []
        self._index = 0
        self._sub_state = False
        self._sub_delay = 0
        self._volume = 100

    def __repr(self):
        return f"{Player.__name__}(id={self.id}, state={self._state}, video_idx={self._index / len(self._queue)})"

    def play(self, video):
        if video not in self._queue:
            raise DomainError(f"playing unknown video: {video}")

        self._index = self._queue.index(video)
        self._state = PlayerState.PLAYING
        self._record(Evt.PlayerStarted, video.id)

    def stop(self):
        if self._state is PlayerState.STOPPED:
            raise DomainError("the player is already stopped")
        self._state = PlayerState.STOPPED
        self._sub_delay = 0
        self._record(Evt.PlayerStopped)

    def queue(self, video, with_priority=False):
        idx = len(self._queue)

        # Try to order videos from the same playlist together
        next_videos = self._queue[self._index :]
        for i, q_video in enumerate(reversed(next_videos)):
            if q_video.playlist_id == video.playlist_id:
                idx = self._index + len(next_videos) - i
                break

        self._queue.insert(idx, video)
        self._record(Evt.VideoQueued, video.id)

    def pause(self):
        if self._state is not PlayerState.PLAYING:
            raise DomainError(f"the player is not playing")
        self._state = PlayerState.PAUSED
        self._record(Evt.PlayerPaused)

    def unpause(self):
        if self._state is not PlayerState.PAUSED:
            raise DomainError(f"the player is not paused")
        self._state = PlayerState.PLAYING
        self._record(Evt.PlayerUnpaused)

    def next_video(self):
        if self._index + 1 >= len(self._queue):
            if config["player.loop_last"] is True:
                return self._queue[self._index]
            return None

        return self._queue[self._index + 1]

    def prev_video(self):
        if self._index == 0:
            return self._queue[0]
        return self._queue[self._index - 1]

    def seek_video(self):
        self._record(Evt.VideoSeeked)

    @property
    def state(self):
        return self._state

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
        self._record(Evt.VolumeUpdated)
