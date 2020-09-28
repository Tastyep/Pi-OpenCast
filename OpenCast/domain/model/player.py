""" Conceptual representation of the media player (VLC) """


from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from OpenCast.config import config
from OpenCast.domain.error import DomainError
from OpenCast.domain.event import player as Evt
from OpenCast.domain.model.video import Video

from . import Id
from .entity import Entity


class State(Enum):
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3


@dataclass
class _Video:
    id: Id
    playlist_id: Optional[Id]


class _VideoSchema(Schema):
    id = fields.UUID()
    playlist_id = fields.UUID(allow_none=True)


class PlayerSchema(Schema):
    id = fields.UUID()
    queue = fields.Nested(_VideoSchema(many=True))
    state = EnumField(State)
    index = fields.Integer()
    sub_state = fields.Bool()
    sub_delay = fields.Integer()
    volume = fields.Integer()

    @post_load
    def make_player(self, data, **_):
        return Player(**data)


class Player(Entity):
    Schema = PlayerSchema

    VOLUME_STEP = 10
    SUBTITLE_DELAY_STEP = 100
    SHORT_TIME_STEP = 1000
    LONG_TIME_STEP = 30000

    @dataclass
    class Data:
        id: Id
        queue: List[_Video] = field(default_factory=list)
        state: State = State.STOPPED
        index: int = 0
        sub_state: bool = True
        sub_delay: int = 0
        volume: int = 70

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)

    @property
    def state(self):
        return self._data.state

    @property
    def video_queue(self):
        return [video.id for video in self._data.queue]

    @property
    def subtitle_state(self):
        return self._data.sub_state

    @property
    def subtitle_delay(self):
        return self._data.sub_delay

    @property
    def volume(self):
        return self._data.volume

    @subtitle_state.setter
    def subtitle_state(self, state):
        self._data.sub_state = state
        self._record(Evt.SubtitleStateUpdated, self._data.sub_state)

    @subtitle_delay.setter
    def subtitle_delay(self, delay):
        self._data.sub_delay = delay
        self._record(Evt.SubtitleDelayUpdated, self._data.sub_delay)

    @volume.setter
    def volume(self, v):
        self._data.volume = max(min(200, v), 0)
        self._record(Evt.VolumeUpdated, self._data.volume)

    def has_video(self, video_id: Id):
        for video in self._data.queue:
            if video.id == video_id:
                return True
        return False

    def play(self, video: Video):
        for i, q_video in enumerate(self._data.queue):
            if q_video.id == video.id:
                self._data.index = i
                self._data.state = State.PLAYING
                self._record(Evt.PlayerStarted, video.id)
                return

        raise DomainError(f"unknown video: {video}")

    def stop(self):
        if self._data.state is State.STOPPED:
            raise DomainError("the player is already stopped")
        self._data.state = State.STOPPED
        self._data.sub_delay = 0
        self._record(Evt.PlayerStopped)

    def queue(self, video: Video, front: bool = False):
        # If the video has already been started, then push the new video after it
        idx = (
            min(
                self._data.index + (self._data.state is not State.STOPPED),
                len(self._data.queue),
            )
            if front
            else len(self._data.queue)
        )

        # Try to order videos from the same playlist together
        if front and video.playlist_id is not None:
            next_reversed = reversed(self._data.queue[idx:])
            for i, q_video in enumerate(next_reversed):
                if q_video.playlist_id == video.playlist_id:
                    idx = len(self._data.queue) - i
                    break

        self._data.queue.insert(idx, _Video(video.id, video.playlist_id))
        self._record(Evt.VideoQueued, video.id)

    def remove(self, video_id: Id):
        count = len(self._data.queue)
        self._data.queue = [video for video in self._data.queue if video.id != video_id]
        if len(self._data.queue) == count:
            raise DomainError(f"unknown video: {video_id}")
        self._record(Evt.VideoRemoved, video_id)

    def next_video(self):
        if self._data.index + 1 >= len(self._data.queue):
            if self._data.queue and config["player.loop_last"] is True:
                return self._data.queue[self._data.index].id
            return None

        return self._data.queue[self._data.index + 1].id

    def toggle_pause(self):
        if self._data.state is State.PLAYING:
            self._data.state = State.PAUSED
        elif self._data.state is State.PAUSED:
            self._data.state = State.PLAYING
        else:
            raise DomainError("the player is not started")
        self._record(Evt.PlayerStateToggled, self._data.state)

    def seek_video(self):
        if self._data.state is State.STOPPED:
            raise DomainError("the player is not started")
        self._record(Evt.VideoSeeked)
