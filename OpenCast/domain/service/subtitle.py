from pathlib import Path

import structlog


class SubtitleService:
    def __init__(self, ffmpeg_wrapper, downloader):
        self._logger = structlog.get_logger(__name__)
        self._ffmpeg_wrapper = ffmpeg_wrapper
        self._downloader = downloader

    def fetch_subtitle(
        self, video, language: str, search_source=True, search_online=True
    ) -> Path:
        subtitle = self._load_from_disk(video.path, language)
        if subtitle is not None:
            return subtitle

        if not video.from_disk():
            subtitle = self._download_from_source(video.source, video.path, language)
            if subtitle is not None:
                return subtitle

        if search_online:
            pass  # TODO

        return None

    def _load_from_disk(self, video_path: Path, language: str) -> str:
        parent_path = video_path.parents[0]
        subtitle = str(video_path.with_suffix(".srt"))

        # Find the matching subtitle from a .srt file
        srtFiles = list(parent_path.glob("*.srt"))
        if Path(subtitle) in srtFiles:
            self._logger.debug("Found srt file", subtitle=subtitle)
            return subtitle

        # Extract file metadata
        # Find subtitle with matching language
        self._logger.debug("Searching softcoded subtitles", subtitle=subtitle)
        metadata = self._ffmpeg_wrapper.probe(video_path)
        for stream in metadata["streams"]:
            self._logger.debug(
                f"Channel #{stream['index']}",
                type=stream["codec_type"],
                name=stream["codec_long_name"],
            )
            if (
                stream["codec_type"] == "subtitle"
                and stream["tags"]["language"] == language
            ):
                self._logger.debug(f"Match: {subtitle}")
                return subtitle
        return None

    def _download_from_source(
        self, video_source: str, video_path: Path, language: str
    ) -> str:
        dest = str(video_path.with_suffix(""))
        subtitle = self._downloader.download_subtitle(
            video_source, dest, language, ["vtt"]
        )
        return subtitle
