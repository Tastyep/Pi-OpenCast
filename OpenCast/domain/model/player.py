from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.event import player_events as e

from .entity import Entity
from .player_state import PlayerState

player_config = config["VideoPlayer"]


class Player(Entity):
    def __init__(self, id_):
        super(Player, self).__init__(id_)
        self._state = PlayerState.STOPPED
        self._queue = []
        self._index = 0
        self._sub_state = False
        self._sub_delay = 0
        self._volume = 100

    def play(self, video=None):
        print("video: {} || active: {}".format(video, self.active_video))
        if video is not None and video != self.active_video:
            self._queue.insert(self._index, video)
        self._state = PlayerState.PLAYING
        self._record(e.PlayerStarted())

    def stop(self):
        if self._state is PlayerState.STOPPED:
            raise DomainError("the player is already stopped")
        self._state = PlayerState.STOPPED
        self._sub_delay = 0
        self._record(e.PlayerStopped())

    def queue(self, video, first=False):
        idx = len(self._queue)
        if first:
            idx = self._index
            if self._state is not PlayerState.STOPPED:
                idx += 1

        # Try to order videos from the same playlist together
        next_videos = self._queue[self._index :]
        for i, q_video in enumerate(reversed(next_videos)):
            if q_video.playlist_id == video.playlist_id:
                idx = self._index + len(next_videos) - i
                break

        self._queue.insert(idx, video)
        self._record(e.VideoQueued())

    def pause(self):
        if self._state is not PlayerState.PLAYING:
            raise DomainError(f"the player is not playing")
        self._state = PlayerState.PAUSED
        self._record(e.PlayerPause())

    def unpause(self):
        if self._state is not PlayerState.PAUSED:
            raise DomainError(f"the player is not paused")
        self._state = PlayerState.PLAYING
        self._record(e.PlayerUnpaused())

    def next_video(self):
        print("IDX: {}, videos: {}".format(self._index, self._queue))
        if self._index + 1 >= len(self._queue):
            if player_config.loop_last is True:
                return self._queue[self._index]
            self.stop()
            return None

        self._index += 1
        return self._queue[self._index]

    def prev_video(self):
        if self._index == 0:
            return self._queue[0]
        self._index -= 1
        return self._queue[self._index]

    def seek_video(self):
        self._record(e.VideoSeeked())

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

    @property
    def active_video(self):
        if self._index < len(self._queue):
            return self._queue[self._index]
        return None

    @subtitle_state.setter
    def subtitle_state(self, state):
        self._sub_state = state
        self._record(e.SubtitleStateUpdated())

    @subtitle_delay.setter
    def subtitle_delay(self, delay):
        self._sub_delay = delay
        self._record(e.SubtitleDelayUpdated())

    @volume.setter
    def volume(self, v):
        self._volume = max(min(200, v), 0)
        self._record(e.VolumeUpdated())
