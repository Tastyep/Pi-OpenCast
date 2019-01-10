import logging
from collections import deque
from threading import (
    Condition,
    Thread,
)

import youtube_dl

from .config import config
from .download_logger import DownloadLogger

logger = logging.getLogger(__name__)
config = config['Downloader']


class VideoDownloader(object):
    def __init__(self):
        self._stopped = False
        self._queue = deque()
        self._cv = Condition()
        self._logger = DownloadLogger()
        self._log_debug = self._logger.is_enabled_for(logging.DEBUG)
        self._thread = Thread(target=self._download_queued_videos)
        self._thread.start()

    def __del__(self):
        with self._cv:
            self._stopped = True
            self._cv.notifyAll()
        self._thread.join()

    def queue(self, videos, dl_callback, first=False):
        with self._cv:
            for video in videos:
                # Position the video with the videos of the same playlist.
                index = 0 if first else len(self._queue)
                if first and video.playlist_id is not None:
                    for i, v in enumerate(reversed(self._queue)):
                        if v[0].playlist_id == video.playlist_id:
                            index = len(self._queue) - i
                            break
                logger.info("[downloader] queue video {}".format(video))
                self._queue.insert(index, (video, dl_callback))
            self._cv.notify()

    def list(self):
        return list(self._queue)

    def extract_playlist(self, url):
        options = {
            'extract_flat': 'in_playlist',
        }
        # Download the playlist data without downloading the videos.
        data = self._fetch_metadata(url, options)
        if data is None:
            return []

        # NOTE(specific) youtube specific
        base_url = url.split('/playlist', 1)[0]
        urls = [base_url + '/watch?v=' + entry['id']
                for entry in data['entries']]
        return urls

    def _download_queued_videos(self):
        while not self._stopped:
            video, dl_callback = (None, None)
            with self._cv:
                while not self._stopped and len(self._queue) == 0:
                    self._cv.wait()
                if self._stopped:
                    return
                video, dl_callback = self._queue.popleft()
            self._download(video, dl_callback)

    def _download(self, video, dl_callback):
        options = {
            'noplaylist': True,
        }
        data = self._fetch_metadata(video.url, options)
        if data is None:
            return

        video.title = data['title']
        video.path = config.output_directory + '/' + video.title + '.mp4'

        def download_hook(d):
            self._logger.log_download(d)

        logger.debug("[downloader] starting download for: {}"
                     .format(video.title))
        options = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                      'bestvideo+bestaudio/best',
            'debug_printtraffic': self._log_debug,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'outtmpl': str(video.path),
            'progress_hooks': [download_hook]
        }
        ydl = youtube_dl.YoutubeDL(options)
        with ydl:  # Download the video
            try:
                ydl.download([video.url])
            except Exception as e:
                logger.error("[downloader] error downloading '{}': {}"
                             .format(video, str(e)))
                return

        logger.debug("[downloader] video downloaded: {}".format(video))
        dl_callback(video)

    def _fetch_metadata(self, url, options):
        logger.debug("[downloader] fetching metadata")
        options.update({
            'ignoreerrors': True,   # Causes ydl to return None on error
            'debug_printtraffic': self._log_debug,
            'logger': logger
        })
        ydl = youtube_dl.YoutubeDL(options)
        with ydl:
            try:
                return ydl.extract_info(url, download=False)
            except Exception as e:
                logger.error("[downloader] error fetch metadata for '{}': {}"
                             .format(url, str(e)))
        return None


def make_video_downloader():
    downloader = VideoDownloader()

    return downloader
