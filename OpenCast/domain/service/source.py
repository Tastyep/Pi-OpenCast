""" Media source operations """

from pathlib import Path
from typing import List

import structlog

from OpenCast.domain.model.video import Stream


class SourceService:
    def __init__(self, downloader, video_parser):
        self._logger = structlog.get_logger(__name__)
        self._downloader = downloader
        self._video_parser = video_parser

    def is_playlist(self, source):
        return "/playlist" in source

    def unfold(self, source):
        return self._downloader.unfold_playlist(source)

    def pick_stream_metadata(self, video):
        if video.from_disk():
            return {"title": Path(video.source).stem}
        return self._downloader.pick_stream_metadata(
            video.source, video.METADATA_FIELDS
        )

    def list_streams(self, video) -> List[Stream]:
        video_path = str(video.path)
        streams = self._video_parser.parse_streams(video_path)
        return [Stream(*stream) for stream in streams]
