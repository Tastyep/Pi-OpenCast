from pathlib import Path

import structlog


class SubtitleService:
    def __init__(self, ffmpeg_wrapper):
        self._logger = structlog.get_logger(__name__)
        self._ffmpeg_wrapper = ffmpeg_wrapper

    def load_from_disk(self, video, language):
        video_name = video.path.name.rsplit(".", 1)[0]
        parent_path = video.path.parents[0]
        subtitle = f"{parent_path}/{video_name}.srt"

        # Find the matching subtitle from a .srt file
        srtFiles = list(parent_path.glob("*.srt"))
        if Path(subtitle) in srtFiles:
            self._logger.debug("Found srt file", subtitle=subtitle)
            return subtitle

        # Extract file metadata
        # Find subtitle with matching language
        self._logger.debug("Searching softcoded subtitles", video=video)
        metadata = self._ffmpeg_wrapper.probe(video.path)
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
                return self._ffmpeg_wrapper.extract_stream(
                    src=video.path,
                    dest=subtitle,
                    stream_idx=stream["index"],
                    override=False,
                )
        return None
