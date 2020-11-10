""" Parse, download and extract a media with its metadata """


from pathlib import Path
from typing import List

import structlog
from hurry.filesize import alternative, size
from youtube_dlc import YoutubeDL
from youtube_dlc.utils import ISO639Utils

from OpenCast.infra import Id
from OpenCast.infra.event.downloader import DownloadError, DownloadSuccess


class Logger:
    def __init__(self, logger):
        self._logger = logger

    def log_download_progress(self, d):
        status = d.get("status", "N/A")
        if status not in ["downloading", "error", "finished"]:
            return

        getattr(self, f"_log_{status}")(d)

    def _log_downloading(self, d):
        filename = d.get("filename", "unknown")
        self._logger.info(
            "Downloading",
            filename=filename,
            ratio=self._format_ratio(d),
            speed=self._format_speed(d),
        )

    def _log_error(self, d):
        filename = d.get("filename", "unknown")
        self._logger.error("Error downloading", filename=filename, error=d)

    def _log_finished(self, d):
        filename = d.get("filename", "unknown")
        total = d.get("total_bytes", 0)
        self._logger.info(
            "Finished downloading",
            filename=filename,
            size=size(total, system=alternative),
        )

    def _format_ratio(self, d):
        downloaded = d.get("downloaded_bytes", None)
        total = d.get("total_bytes", None)
        if downloaded is None or total is None:
            return "N/A"

        return "{0:.2f}%".format(100 * (downloaded / total))

    def _format_speed(self, d):
        speed = d.get("speed", 0)
        if speed is None:
            speed = 0
        return "{}/s".format(size(speed, system=alternative))


class Downloader:
    def __init__(self, executor, evt_dispatcher):
        self._executor = executor
        self._evt_dispatcher = evt_dispatcher
        self._logger = structlog.get_logger(__name__)
        self._dl_logger = Logger(self._logger)

    def download_video(self, op_id: Id, source: str, dest: str):
        def impl():
            self._logger.debug("Downloading", video=dest)
            options = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "bestvideo+bestaudio/best",
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
                self._evt_dispatcher.dispatch(DownloadError(op_id, error))
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
