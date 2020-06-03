from threading import Lock
from uuid import UUID

import OpenCast.infra.event.player as e
import structlog
import vlc


class PlayerWrapper:
    def __init__(self, evt_dispatcher):
        self._logger = structlog.get_logger(__name__)
        self._evt_dispatcher = evt_dispatcher

        self._instance = vlc.Instance()
        self._player = self._instance.media_player_new()
        # self._list_player = self._instance.media_list_player_new()
        # self._list_player.set_media_player(self._player)
        # self._playlist = self._instance.media_list_new()
        # self._list_player.set_media_list(self._playlist)
        self._id_to_media = {}

        self._lock = Lock()
        self._stop_operation_id = None

        player_events = self._player.event_manager()
        player_events.event_attach(
            vlc.EventType.MediaPlayerEndReached, self._on_media_end
        )

    def play(self, video_id: UUID, video_path: str):
        media = self._id_to_media.get(video_id, None)
        if media is None:
            media = self._instance.media_new(video_path)
            self._id_to_media[video_id] = media
        print(f"Play video {video_id}")
        self._player.set_media(media)
        self._player.play()

    def stop(self):
        self._player.stop()

    def pause(self):
        self._player.pause()

    def unpause(self):
        self._player.pause()

    def toggle_subtitle(self):
        self._player.toggle_teletext()

    def set_subtitle_delay(self, delay: int):
        self._player.video_set_spu_delay(delay)

    def set_volume(self, volume):
        self._player.audio_set_volume(volume)

    def seek(self, duration):
        current_time = self._player.get_time()
        if current_time != -1:
            self._player.set_time(current_time + duration)

    def _on_media_end(self, event):
        evt = e.MediaEndReached(None)
        self._evt_dispatcher.dispatch(evt)
