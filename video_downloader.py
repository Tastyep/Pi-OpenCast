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
                logger.info("[downloader] queue video %r" % (video, index))
                self._queue.insert(index, (video, dl_callback))
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
        logger.debug("[downloader] starting download for: %r" % (video.title))
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
        logger.debug("[downloader] video downloaded: %r" % (video))
        dl_callback(video)


def make_video_downloader():
    downloader = VideoDownloader()

    return downloader
