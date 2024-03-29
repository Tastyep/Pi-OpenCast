""" Conceptual representation of the media player (VLC) """


from dataclasses import dataclass
from enum import Enum
from typing import Optional

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from OpenCast.domain.error import DomainError
from OpenCast.domain.event import player as Evt

from . import Id
from .entity import Entity


class State(Enum):
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3


class PlayerSchema(Schema):
    id = fields.UUID()
    queue = fields.UUID()
    state = EnumField(State)
    video_id = fields.UUID(allow_none=True)
    sub_state = fields.Bool()
    sub_delay = fields.Integer()
    volume = fields.Integer()


class Player(Entity):
    Schema = PlayerSchema

    @dataclass
    class Data:
        id: Id
        queue: Id
        state: State = State.STOPPED
        video_id: Optional[Id] = None
        sub_state: bool = True
        sub_delay: int = 0
        volume: int = 70

    def __init__(self, *attrs, **kattrs):
        super().__init__(self.Data, *attrs, **kattrs)
        self._record(
            Evt.PlayerCreated,
            self._data.queue,
            self._data.state,
            self._data.sub_state,
            self._data.sub_delay,
            self._data.volume,
        )

    @property
    def queue(self):
        return self._data.queue

    @property
    def state(self):
        return self._data.state

    @property
    def video_id(self):
        return self._data.video_id

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

    @state.setter
    def state(self, state):
        if state == self._data.state:
            return

        old_state = self._data.state
        self._data.state = state
        self._record(Evt.PlayerStateUpdated, old_state, self._data.state)

    def play(self, video_id: Id):
        if self._data.state is not State.STOPPED:
            raise DomainError("the player is already started", state=self._data.state)

        self._data.video_id = video_id
        self._record(Evt.PlayerVideoUpdated, None, self._data.video_id)

        self.state = State.PLAYING

    def stop(self):
        if self._data.state is State.STOPPED:
            raise DomainError("the player is not started")

        self.state = State.STOPPED

        old_video_id = self._data.video_id
        self._data.video_id = None
        self._data.sub_delay = 0
        self._record(Evt.PlayerVideoUpdated, old_video_id, self._data.video_id)

    def toggle_pause(self):
        if self._data.state is State.PLAYING:
            self.state = State.PAUSED
        elif self._data.state is State.PAUSED:
            self.state = State.PLAYING
        else:
            raise DomainError("the player is not started")

    def seek_video(self, duration):
        if self._data.state is State.STOPPED:
            raise DomainError("the player is not started")
        self._record(Evt.VideoSeeked, duration)
