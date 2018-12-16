import youtube_dl
import logging
import time

from threading import Thread, Condition
from collections import deque
from .config import config
from .download_logger import DownloadLogger

logger = logging.getLogger(__name__)
config = config["Downloader"]


class VideoDownloader(object):
    def __init__(self):
        self._stopped = False
        self._queue = deque()
        self._cv = Condition()
        self._logger = DownloadLogger()
        self._thread = Thread(target=self._download_queued_videos)
        self._thread.start()

    def __del__(self):
        with self._cv:
            self._stopped = True
            self._cv.notifyAll()
        self._thread.join()

    def queue(self, videos, dl_callback, first=False):
        Thread(target=self._queue_downloads,
               args=(videos, dl_callback, first,)).start()

    def list_queue(self):
        return list(self._queue)

    def _fetch_metadata(self, video):
        ydl = youtube_dl.YoutubeDL(
            {
                'noplaylist': True,
                'ignoreerrors': True,
                'debug_printtraffic': False,
                'logger': logger
            })
        with ydl:  # Download the video data without downloading it.
            data = ydl.extract_info(video.url, download=False)
        if data is not None:
            video.title = data['title']
            return True
        return False

    def _queue_downloads(self, videos, dl_callback, first):
        for video in videos:
            with self._cv:
                if not self._fetch_metadata(video):
                    continue
                # Position the video with the videos of the same playlist.
                index = 0 if first else len(self._queue)
                if first and video.playlistId is not None:
                    for i, v in enumerate(reversed(self._queue)):
                        if v[0].playlistId == video.playlistId:
                            index = len(self._queue) - i
                            break
                logger.info("[downloader] queue video %r" % (video))
                self._queue.insert(index, (video, dl_callback))
                self._cv.notify()
            time.sleep(0.1)

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
        video.path = config.output_directory + '/' + video.title + '.mp4'

        def download_hook(d):
            self._logger.log_download(d)

        logger.debug("[downloader] starting download for: %r" % (video.title))
        ydl = youtube_dl.YoutubeDL({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                      'bestvideo+bestaudio/best',
            'noplaylist': True,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'outtmpl': str(video.path),
            'progress_hooks': [download_hook]
        })
        with ydl:  # Download the video
            ydl.download([video.url])
        logger.debug("[downloader] video downloaded: %r" % (video))
        dl_callback(video)


def make_video_downloader():
    downloader = VideoDownloader()

    return downloader
