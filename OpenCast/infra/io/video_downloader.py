import youtube_dl

import structlog
from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess

from .download_logger import DownloadLogger


class VideoDownloader:
    def __init__(self, evt_dispatcher, executor):
        self._evt_dispatcher = evt_dispatcher
        self._executor = executor
        self._logger = structlog.get_logger(__name__)
        self._dl_logger = DownloadLogger(self._logger)
        self._log_debug = False  # self._dl_logger.is_enabled_for(logging.DEBUG)

    def download(self, op_id, video):
        def impl():
            self._logger.debug("Downloading", video=video)
            options = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "bestvideo+bestaudio/best",
                "debug_printtraffic": self._log_debug,
                "noplaylist": True,
                "merge_output_format": "mp4",
                "outtmpl": str(video.path),
                "quiet": True,
                "progress_hooks": [self._dl_logger.log_progress],
            }
            ydl = youtube_dl.YoutubeDL(options)
            with ydl:  # Download the video
                try:
                    ydl.download([video.source])
                except Exception as e:
                    self._logger.error("Download error", video=video, error=e)
                    self._evt_dispatcher.dispatch(DownloadError(op_id, str(e)))
                    return

            self._logger.debug("Download success", video=video)
            self._evt_dispatcher.dispatch(DownloadSuccess(op_id))

        self._logger.debug("Queing", video=video)
        self._executor.submit(impl)

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

    def _fetch_metadata(self, url, options):
        self._logger.debug("Fetching metadata", url=url)
        options.update(
            {
                "ignoreerrors": True,  # Causes ydl to return None on error
                "debug_printtraffic": self._log_debug,
                "quiet": True,
                "progress_hooks": [self._dl_logger.log_progress],
            }
        )
        ydl = youtube_dl.YoutubeDL(options)
        with ydl:
            try:
                return ydl.extract_info(url, download=False)
            except Exception as e:
                self._logger.error("Fetching metadata error", url=url, error=e)
        return None
