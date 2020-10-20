from pathlib import Path
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.domain.model.video import Stream
from OpenCast.domain.service.source import SourceService


class SourceServiceTest(TestCase):
    def setUp(self):
        self.downloader = Mock()
        self.video_parser = Mock()
        self.service = SourceService(self.downloader, self.video_parser)

    def test_is_playlist(self):
        self.assertTrue(
            self.service.is_playlist("https://www.youtube.com/playlist?list=id")
        )
        self.assertFalse(
            self.service.is_playlist(
                "https://www.youtube.com/watch?v=id&list=id&index=2"
            )
        )

    def test_pick_stream_metadata(self):
        self.downloader.pick_stream_metadata.return_value = {
            "source_protocol": "http",
            "title": "test",
            "collection_name": "collection",
            "thumbnail": "url",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": "http",
            "title": "test",
            "collection_name": "collection",
            "thumbnail": "url",
        }
        self.assertEqual(expected, metadata)

    def test_pick_stream_metadata_partial(self):
        self.downloader.pick_stream_metadata.return_value = {
            "title": "test",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": None,
            "title": "test",
            "collection_name": None,
            "thumbnail": None,
        }
        self.assertEqual(expected, metadata)

    def test_pick_stream_metadata_alternative_fields(self):
        self.downloader.pick_stream_metadata.return_value = {
            "protocol": "http",
            "title": "test",
            "album": "album_name",
            "thumbnail": "url",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": "http",
            "title": "test",
            "collection_name": "album_name",
            "thumbnail": "url",
        }
        self.assertEqual(expected, metadata)

    def test_pick_file_metadata(self):
        metadata = self.service.pick_file_metadata(Path("/tmp/video.mp4"))
        expected = {
            "source_protocol": None,
            "title": "video",
            "collection_name": None,
            "thumbnail": None,
        }
        self.assertEqual(expected, metadata)

    def test_list_streams(self):
        video = Mock()
        video.Path = Path("/tmp/toto.mp4")

        streams = [
            (0, "video", "video_lang"),
            (1, "audio", "audio_lang"),
            (2, "subtitle", "subtitle_lang"),
        ]
        self.video_parser.parse_streams.return_value = streams

        expected = [Stream(*stream) for stream in streams]
        stream_list = self.service.list_streams(video)
        self.assertEqual(expected, stream_list)
