""" Media source operations """

from pathlib import Path
from typing import List, Optional

import structlog

from OpenCast.domain.model.video import Stream, Video


class SourceService:
    def __init__(self, downloader, video_parser):
        self._logger = structlog.get_logger(__name__)
        self._downloader = downloader
        self._video_parser = video_parser
        self._metadata_mapper = {
            "source_protocol": ["protocol"],
            "collection_name": ["album"],
        }

    def is_playlist(self, source: str) -> bool:
        data = self._downloader.download_metadata(source, process_ie_data=False)
        if data is None:
            return False

        return data.get("_type", None) == "playlist"

    def unfold(self, source: str) -> List[str]:
        self._logger.info("Unfolding playlist", url=source)
        data = self._downloader.download_metadata(source, process_ie_data=True)
        if data is None:
            return []

        entries = data.get("entries", [])
        return [entry["webpage_url"] for entry in entries if "webpage_url" in entry]

    def pick_stream_metadata(self, source: str) -> Optional[dict]:
        data = self._downloader.download_metadata(source, process_ie_data=True)
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

    def pick_file_metadata(self, source: Path) -> dict:
        metadata = {field: None for field in Video.METADATA_FIELDS}
        metadata["title"] = source.stem
        return metadata

    def fetch_stream_link(self, source: str) -> Optional[str]:
        data = self._downloader.download_metadata(source, process_ie_data=True)
        if data is None:
            return None

        return data.get("url", None)

    def list_streams(self, video) -> List[Stream]:
        video_path = video.location
        streams = self._video_parser.parse_streams(video_path)
        return [Stream(*stream) for stream in streams]
