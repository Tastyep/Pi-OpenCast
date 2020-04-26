import logging
from threading import Condition, Thread

import youtube_dl

from .download_logger import DownloadLogger

logger = logging.getLogger(__name__)


class VideoDownloader:
    def __init__(self):
        self._stopped = False
        self._queue = []
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

    def queue(self, video, dl_callback, priority=False):
        with self._cv:
            # Position the video with videos from the same playlist.
            index = 0 if priority else len(self._queue)
            if priority and video.playlist_id is not None:
                for i, v in enumerate(reversed(self._queue)):
                    if v[0].playlist_id == video.playlist_id:
                        index = len(self._queue) - i
                        break
            logger.debug(f"queue video {video}")
            self._queue.insert(index, (video, dl_callback))
            self._cv.notify()

    def fetch_metadata(self, url, fields):
        options = {
            "noplaylist": True,
        }
        data = self._fetch_metadata(url, options)
        if data is None:
            return None
        return {k: data[k] for k in fields}

    def unfold_playlist(self, url):
        options = {
            "extract_flat": "in_playlist",
        }
        # Download the playlist data without downloading the videos.
        data = self._fetch_metadata(url, options)
        if data is None:
            return []

        # NOTE(specific) youtube specific
        base_url = url.split("/playlist", 1)[0]
        urls = [base_url + "/watch?v=" + entry["id"] for entry in data["entries"]]
        return urls

    def _download_queued_videos(self):
        while not self._stopped:
            video, dl_callback = (None, None)
            with self._cv:
                while not self._stopped and len(self._queue) == 0:
                    self._cv.wait()
                if self._stopped:
                    return
                video, dl_callback = self._queue.pop(0)
            self._download(video, dl_callback)

    def _download(self, video, dl_callback):
        def progress_hook(d):
            self._logger.log_download(d)

        logger.debug(f"starting download for: {video.title}")
        options = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
            "bestvideo+bestaudio/best",
            "debug_printtraffic": self._log_debug,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "outtmpl": str(video.path),
            "progress_hooks": [progress_hook],
        }
        ydl = youtube_dl.YoutubeDL(options)
        with ydl:  # Download the video
            try:
                ydl.download([video.source])
            except Exception as e:
                logger.error(f"error downloading {video}: {e}")
                return

        logger.debug(f"video downloaded: {video}")
        dl_callback(video)

    def _fetch_metadata(self, url, options):
        logger.debug(f"fetching metadata")
        options.update(
            {
                "ignoreerrors": True,  # Causes ydl to return None on error
                "debug_printtraffic": self._log_debug,
                "logger": logger,
            }
        )
        ydl = youtube_dl.YoutubeDL(options)
        with ydl:
            try:
                return ydl.extract_info(url, download=False)
            except Exception as e:
                logger.error(f"error fetching metadata for '{url}': {e}")
        return None
