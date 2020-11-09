""" Parse, download and extract a media with its metadata """


from pathlib import Path
from typing import List

import structlog
from youtube_dlc import YoutubeDL
from youtube_dlc.utils import ISO639Utils

from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess

from .download_logger import DownloadLogger


class Downloader:
    def __init__(self, executor, evt_dispatcher):
        self._executor = executor
        self._evt_dispatcher = evt_dispatcher
        self._logger = structlog.get_logger(__name__)
        self._dl_logger = DownloadLogger(self._logger)
        self._log_debug = False  # self._dl_logger.is_enabled_for(logging.DEBUG)

    def download_video(self, op_id, source: str, dest: str):
        def impl():
            self._logger.debug("Downloading", video=dest)
            options = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "bestvideo+bestaudio/best",
                "debug_printtraffic": self._log_debug,
                "noplaylist": True,
                "merge_output_format": "mp4",
                "outtmpl": dest,
                "quiet": True,
                "progress_hooks": [self._dl_logger.log_download_progress],
            }
            ydl = YoutubeDL(options)
            with ydl:  # Download the video
                try:
                    ydl.download([source])
                except Exception as e:
                    self._logger.error(
                        "Download error", video=dest, source=source, error=e
                    )
                    self._evt_dispatcher.dispatch(DownloadError(op_id, str(e)))
                    return

            if not Path(dest).exists():
                error = "video path points to non existent file"
                self._logger.error(
                    "Download error",
                    video=dest,
                    source=source,
                    error=error,
                )
                self._evt_dispatcher.dispatch(DownloadError(op_id, str(error)))
                return

            self._logger.debug("Download success", video=dest)
            self._evt_dispatcher.dispatch(DownloadSuccess(op_id))

        self._logger.debug("Queing", video=dest)
        self._executor.submit(impl)

    def download_subtitle(self, url: str, dest: str, lang: str, exts: List[str]):
        self._logger.debug("Downloading subtitle", subtitle=dest, lang=lang)

        lang = ISO639Utils.long2short(lang)
        for ext in exts:
            options = {
                "skip_download": True,
                "subtitleslangs": [lang],
                "subtitlesformat": ext,
                "writeautomaticsub": False,
                "outtmpl": dest,
                "progress_hooks": [self._dl_logger.log_download_progress],
                "quiet": True,
            }
            ydl = YoutubeDL(options)
            with ydl:
                try:
                    ydl.download([url])
                    return f"{dest}.{lang}.{ext}"
                except Exception as e:
                    self._logger.error(
                        "Subtitle download error", subtitle=dest, ext=ext, error=e
                    )
        return None

    def download_metadata(self, url: str, process_ie_data: bool):
        self._logger.debug("Downloading metadata", url=url)
        options = {
            "noplaylist": True,  # Allow getting the _type value set to URL when passing a playlist entry
            "extract_flat": False,
            "ignoreerrors": True,  # Causes ydl to return None on error
            "debug_printtraffic": self._log_debug,
            "quiet": True,
            "progress_hooks": [self._dl_logger.log_download_progress],
        }
        ydl = YoutubeDL(options)
        with ydl:
            try:
                return ydl.extract_info(url, download=False, process=process_ie_data)
            except Exception as e:
                self._logger.error("Downloading metadata error", url=url, error=e)
        return None
