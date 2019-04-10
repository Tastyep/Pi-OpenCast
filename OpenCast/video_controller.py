import logging
import uuid

from . import (
    player_wrapper,
    video_downloader,
)
from .video import Video

logger = logging.getLogger(__name__)


class VideoController(object):
    def __init__(self, player, downloader):
        self._player = player
        self._downloader = downloader

    def stream_video(self, url):
        logger.debug("[controller] stream video, URL='{}'".format(url))
        self._player.stop(stop_browsing=True)

        video = Video(url)
        if video.is_local():
            self._player.play(video)
            return

        self._queue_video(video, self._play_video, first=True)

    def queue_video(self, url):
        logger.debug("[controller] queue video, URL='{}'".format(url))

        video = Video(url)
        if video.is_local():
            self._player.queue(video)
            return

        self._queue_video(video, self._player.queue, first=False)

    def stop_video(self):
        logger.debug("[controller] stop current video")
        self._player.stop()

    def prev_video(self):
        logger.debug("[controller] prev video")
        self._player.prev()

    def next_video(self):
        logger.debug("[controller] next video")
        self._player.next()

    def play_pause_video(self):
        self._player.play_pause()

    def toggle_subtitle(self):
        self._player.toggle_subtitle()

    def shift_subtitle(self, increase):
        if increase:
            self._player.increase_subtitle_delay()
        else:
            self._player.decrease_subtitle_delay()

    def change_volume(self, increase):
        self._player.change_volume(increase)
        logger.debug("[controller] change player volume, increase: {}"
                     .format(increase))

    def seek_time(self, forward, long):
        logger.debug("[controller] seek video time, forward={}, long={}"
                     .format(forward, long))
        self._player.seek(forward, long)

    # Getter methods

    def list_queued_videos(self):
        videos = self._player.get_queue()
        videos.extend(self._downloader.get_queue())

        return videos

    # Private methods

    def _play_video(self, video):
        self._player.queue(video, first=True)
        self._player.play()

    def _queue_video(self, video, dl_callback, first):
        if '/playlist' in video.url:
            logger.debug("[controller] playlist detected, unfolding...")
            # Generate a unique ID for the playlist
            playlist_id = uuid.uuid4()
            urls = self._downloader.extract_playlist(video.url)
            videos = [Video(u, playlist_id) for u in urls]
            logger.debug("[controller] playlist url unfolded to {}"
                         .format(videos))
            self._downloader.queue(videos, dl_callback, first)
        else:
            logger.debug("[controller] queue single video: {}".format(video))
            self._downloader.queue([video], dl_callback, first)


def make_video_controller():
    player = player_wrapper.make_wrapper()
    downloader = video_downloader.make_video_downloader()

    return VideoController(player, downloader)
