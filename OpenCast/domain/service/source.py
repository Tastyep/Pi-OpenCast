""" Media source operations """

from pathlib import Path
from typing import List

import structlog

from OpenCast.domain.model.video import Stream, Video


class SourceService:
    def __init__(self, downloader, video_parser):
        self._logger = structlog.get_logger(__name__)
        self._downloader = downloader
        self._video_parser = video_parser
        self._metadata_mapper = {"collection_name": ["album"]}

    def is_playlist(self, source):
        return "/playlist" in source

    def unfold(self, source):
        return self._downloader.unfold_playlist(source)

    def pick_stream_metadata(self, source: str):
        data = self._downloader.pick_stream_metadata(source)
        if data is None:
            return None

        metadata = {field: None for field in Video.METADATA_FIELDS}
        for field in Video.METADATA_FIELDS:
            if field in data:
                metadata[field] = data.get(field, None)
            elif field in self._metadata_mapper:
                for alt_field in self._metadata_mapper[field]:
                    if alt_field in data:
                        metadata[field] = data[alt_field]
                        break

        return metadata

    def pick_file_metadata(self, source: Path):
        metadata = {field: None for field in Video.METADATA_FIELDS}
        metadata["title"] = source.stem
        return metadata

    def list_streams(self, video) -> List[Stream]:
        video_path = video.location
        streams = self._video_parser.parse_streams(video_path)
        return [Stream(*stream) for stream in streams]
