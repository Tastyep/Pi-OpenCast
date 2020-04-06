import logging
from pathlib import Path


class SubtitleService:
    def __init__(self, ffmpeg_wrapper):
        self._logger = logging.getLogger(__name__)
        self._ffmpeg_wrapper = ffmpeg_wrapper

    def load_from_disk(self, video, language):
        video_name = video.path.name.rsplit(".", 1)[0]
        parent_path = video.path.parents[0]
        subtitle = f"{parent_path}/{video_name}.srt"

        # Find the matching subtitle from a .srt file
        srtFiles = list(parent_path.glob("*.srt"))
        if Path(subtitle) in srtFiles:
            self._logger.debug(f"matching susbtitle file: {subtitle}")
            return subtitle

        # Extract file metadata
        # Find subtitle with matching language
        self._logger.debug(f"searching softcoded subtitles from {video}")
        metadata = self._ffmpeg_wrapper.probe(video.path)
        for stream in metadata["streams"]:
            self._logger.debug(f"{stream}")
            if (
                stream["codec_type"] == "subtitle"
                and stream["tags"]["language"] == language
            ):
                self._logger.info(f"match: {subtitle}")
                return self._ffmpeg_wrapper.extract_stream(
                    src=video.path,
                    dest=subtitle,
                    stream_idx=stream["index"],
                    override=False,
                )
        return None
