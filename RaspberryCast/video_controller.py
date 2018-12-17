import logging
import youtube_dl
import uuid

from . import media_player
from . import video_downloader
from .video import Video

logger = logging.getLogger(__name__)


class VideoController(object):
    def __init__(self):
        self._player = media_player.make_player(1.0)
        self._downloader = video_downloader.make_video_downloader()

    def stream_video(self, url):
        logger.debug("[controller] stream video, URL='{}'".format(url))
        self._player.stop()

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

    def play_pause_video(self, pause):
        self._player.play_pause()

    def change_volume(self, increase):
        self._player.change_volume(increase)
        logger.debug("[controller] change player volume, volume={}"
                     .format(self._player.volume))

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
            playlistId = uuid.uuid4()
            urls = self._parse_playlist(video.url)
            videos = [Video(u, playlistId) for u in urls]
            logger.debug("[controller] playlist url unfolded to {}"
                         .format(videos))
            self._downloader.queue(videos, dl_callback, first)
        else:
            logger.debug("[controller] queue single video: {}".format(video))
            self._downloader.queue([video], dl_callback, first)

    def _parse_playlist(self, url):
        ydl_opts = {
            'ignoreerrors': True,
            'extract_flat': 'in_playlist',
            'logger': logger
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        with ydl:  # Download the playlist data without downloading the videos.
            data = ydl.extract_info(url, download=False)

        base_url = url.split('/playlist', 1)[0]
        urls = [base_url + '/watch?v=' + entry['id']
                for entry in data['entries']]
        return urls


def make_video_controller():
    return VideoController()
