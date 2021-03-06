""" Media player abstraction """

from threading import Condition

import structlog
from vlc import EventType

import OpenCast.infra.event.player as e

from .error import PlayerError


class PlayerWrapper:
    def __init__(self, vlc_instance, evt_dispatcher):
        self._logger = structlog.get_logger(__name__)

        self._instance = vlc_instance
        self._evt_dispatcher = evt_dispatcher

        self._player = self._instance.media_player_new()

        player_events = self._player.event_manager()
        player_events.event_attach(EventType.MediaPlayerEndReached, self._on_media_end)

    def play(self, location: str, stream: bool):
        media = (
            self._instance.media_new_location(location)
            if stream
            else self._instance.media_new_path(location)
        )
        self._player.set_media(media)
        media.release()
        self._player.play()

    def stop(self):
        self._player.stop()

    def pause(self):
        self._player.pause()

    def unpause(self):
        self._player.pause()

    def select_subtitle_stream(self, index: int):
        media = self._player.get_media()
        if media is None:
            raise PlayerError("the player is not started")

        def is_playing(_, cv):
            with cv:
                cv.notify()

        cv = Condition()
        self._player.event_manager().event_attach(
            EventType.MediaPlayerPlaying, is_playing, cv
        )
        with cv:
            cv.wait_for(self._player.is_playing)
        self._player.video_set_spu(index)

    def toggle_subtitle(self):
        self._player.toggle_teletext()

    def set_subtitle_delay(self, delay: int):
        self._player.video_set_spu_delay(delay * 1000)

    def set_volume(self, volume):
        self._player.audio_set_volume(volume)

    def seek(self, duration):
        current_time = self._player.get_time()
        if current_time != -1:
            self._player.set_time(current_time + duration)

    def _on_media_end(self, event):
        evt = e.MediaEndReached(None)
        self._evt_dispatcher.dispatch(evt)
