import youtube_dl
import logging

from threading import Thread, Condition
from collections import deque

logger = logging.getLogger("App")


class VideoDownloader(object):
    def __init__(self):
        self._stopped = False
        self._queue = deque()
        self._cv = Condition()
        self._thread = Thread(target=self._download_queued_videos)
        self._thread.start()

    def __del__(self):
        with self._cv:
            self._stopped = True
            self._cv.notifyAll()
        self._thread.join()

    def queue(self, videos, dl_callback, first=False):
        logger.debug("[player] Queue videos: %r" % (videos))
        Thread(target=self._queue_downloads,
               args=(videos, dl_callback, first,)).start()

    def list_queue(self):
        return list(self._queue)

    def _fetch_metadata(self, video):
        ydl = youtube_dl.YoutubeDL(
            {
                'noplaylist': True,
                'ignoreerrors': True,
            })
        with ydl:  # Download the video data without downloading it.
            data = ydl.extract_info(video.url, download=False)
        video.title = data['title']

        return data is not None

    def _queue_downloads(self, videos, dl_callback, first):
        with self._cv:
            accessible_videos = [(video, dl_callback) for video in videos
                                 if self._fetch_metadata(video)]
            if first:
                self._queue.extendleft(reversed(accessible_videos))
            else:
                self._queue.extendRight(accessible_videos)
            self._cv.notify()

    def _download_queued_videos(self):
        while not self._stopped:
            with self._cv:
                while len(self._queue) == 0 and not self._stopped:
                    self._cv.wait()
                if self._stopped:
                    return
                video, dl_callback = self._queue.popleft()
            self._download(video, dl_callback)

    def _download(self, video, dl_callback):
        video.path = '/tmp/' + video.title + '.mp4'
        ydl = youtube_dl.YoutubeDL({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                      'bestvideo+bestaudio/best',
            'noplaylist': True,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'outtmpl': str(video.path)
        })
        with ydl:  # Download the video
            ydl.download([video.url])
        dl_callback(video)


def make_video_downloader():
    downloader = VideoDownloader()

    return downloader
