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
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'logger': logger
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        with ydl:  # Download the playlist data without downloading the videos.
            data = ydl.extract_info(url, download=False)

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
        if not self._fetch_metadata(video):
            return

        video.path = config.output_directory + '/' + video.title + '.mp4'

        def download_hook(d):
            self._logger.log_download(d)

        logger.debug("[downloader] starting download for: {}"
                     .format(video.title))
        ydl = youtube_dl.YoutubeDL({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                      'bestvideo+bestaudio/best',
            'debug_printtraffic': self._log_debug,
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'outtmpl': str(video.path),
            'progress_hooks': [download_hook]
        })
        with ydl:  # Download the video
            ydl.download([video.url])
        logger.debug("[downloader] video downloaded: {}".format(video))
        dl_callback(video)

    def _fetch_metadata(self, video):
        logger.debug("[downloader] fetching metadata")
        ydl = youtube_dl.YoutubeDL(
            {
                'noplaylist': True,
                'debug_printtraffic': self._log_debug,
                'logger': logger
            })
        with ydl:  # Download the video data without downloading it.
            data = ydl.extract_info(video.url, download=False)
        if data is None:
            return False

        video.title = data['title']
        return True


def make_video_downloader():
    downloader = VideoDownloader()

    return downloader
