""" Player external operations """

from typing import List

import structlog

from OpenCast.config import config
from OpenCast.domain.model import Id
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.playlist import Playlist


class QueueingService:
    def __init__(self, player_repo, playlist_repo):
        self._logger = structlog.get_logger(__name__)
        self._player_repo = player_repo
        self._playlist_repo = playlist_repo

    def queue(
        self, playlist: Playlist, video_id: Id, front: bool, prev_video_id: Id
    ) -> List[Id]:
        if not front:
            playlist.ids.append(video_id)
            return playlist.ids

        player = self._player_repo.get_player()
        player_started = player.state is not PlayerState.STOPPED
        player_video_idx = (
            0
            if player.video_id not in playlist.ids
            else playlist.ids.index(player.video_id)
        )
        # Position the video after the one currently playing
        video_idx = min(player_video_idx + player_started, len(playlist.ids))

        # Order videos of the same collection together
        if prev_video_id in playlist.ids:
            video_idx = max(video_idx, playlist.ids.index(prev_video_id) + 1)

        playlist.ids.insert(video_idx, video_id)
        return playlist.ids

    def next_video(self, playlist_id: Id, video_id: Id) -> Id:
        playlist = self._playlist_repo.get(playlist_id)
        if video_id not in playlist.ids:
            self._logger.warning("unknown video", video=video_id, playlist=playlist)
            return None

        video_idx = playlist.ids.index(video_id)
        if video_idx + 1 < len(playlist.ids):
            return playlist.ids[video_idx + 1]

        if config["player.loop_last"] is True:
            return playlist.ids[video_idx]
        return None
