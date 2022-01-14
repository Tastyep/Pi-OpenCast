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

    def test_is_playlist_with_playlist(self):
        self.downloader.download_metadata.return_value = {
            "_type": "playlist",
        }

        self.assertTrue(
            self.service.is_playlist("https://www.youtube.com/playlist?list=id")
        )

    def test_is_playlist_with_video(self):
        self.downloader.download_metadata.return_value = {
            "_type": "video",
        }

        self.assertFalse(
            self.service.is_playlist(
                "https://www.youtube.com/watch?v=ciXp&list=cCY&index=1"
            )
        )

    def test_is_playlist_no_metadata(self):
        self.downloader.download_metadata.return_value = None

        self.assertFalse(
            self.service.is_playlist(
                "https://www.youtube.com/watch?v=ciXp&list=cCY&index=1"
            )
        )

    def test_unfold(self):
        self.downloader.download_metadata.return_value = {
            "entries": [
                {"webpage_url": "url1"},
                {"webpage_url": "url2"},
            ],
        }

        self.assertEqual(
            ["url1", "url2"],
            self.service.unfold("https://www.youtube.com/playlist?list=id"),
        )

    def test_unfold_partial_metadata(self):
        self.downloader.download_metadata.return_value = {
            "entries": [],
        }

        self.assertEqual(
            [],
            self.service.unfold("https://www.youtube.com/playlist?list=id"),
        )

    def test_unfold_no_metadata(self):
        self.downloader.download_metadata.return_value = None

        self.assertEqual(
            [],
            self.service.unfold("https://www.youtube.com/playlist?list=id"),
        )

    def test_pick_stream_metadata(self):
        self.downloader.download_metadata.return_value = {
            "source_protocol": "http",
            "title": "test",
            "duration": 300,
            "artist": "artist",
            "album": "album",
            "thumbnail": "url",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": "http",
            "title": "test",
            "duration": 300,
            "artist": "artist",
            "album": "album",
            "thumbnail": "url",
        }
        self.assertEqual(expected, metadata)

    def test_pick_stream_metadata_partial(self):
        self.downloader.download_metadata.return_value = {
            "title": "test",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": None,
            "title": "test",
            "duration": None,
            "artist": None,
            "album": None,
            "thumbnail": None,
        }
        self.assertEqual(expected, metadata)

    def test_pick_stream_metadata_post_processed(self):
        self.downloader.download_metadata.return_value = {
            "artist": "toto, band members",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": None,
            "title": None,
            "duration": None,
            "artist": "toto",
            "album": None,
            "thumbnail": None,
        }
        self.assertEqual(expected, metadata)

    def test_pick_stream_metadata_alternative_fields(self):
        self.downloader.download_metadata.return_value = {
            "protocol": "http",
            "title": "test",
            "duration": 300,
            "artist": "artist",
            "album": "album_name",
            "thumbnail": "url",
        }
        metadata = self.service.pick_stream_metadata("source")
        expected = {
            "source_protocol": "http",
            "title": "test",
            "duration": 300,
            "artist": "artist",
            "album": "album_name",
            "thumbnail": "url",
        }
        self.assertEqual(expected, metadata)

    def test_pick_stream_metadata_no_metadata(self):
        self.downloader.download_metadata.return_value = None
        metadata = self.service.pick_stream_metadata("source")
        self.assertEqual(None, metadata)

    def test_pick_file_metadata(self):
        metadata = self.service.pick_file_metadata(Path("/tmp/video.mp4"))
        expected = {
            "source_protocol": None,
            "title": "video",
            "duration": None,
            "artist": None,
            "album": None,
            "thumbnail": None,
        }
        self.assertEqual(expected, metadata)

    def test_fetch_stream_link(self):
        self.downloader.download_metadata.return_value = {
            "url": "test_url",
        }
        url = self.service.fetch_stream_link("source")
        self.assertEqual("test_url", url)

    def test_fetch_stream_link_missing(self):
        self.downloader.download_metadata.return_value = {}
        url = self.service.fetch_stream_link("source")
        self.assertEqual(None, url)

    def test_fetch_stream_link_no_metadata(self):
        self.downloader.download_metadata.return_value = None
        url = self.service.fetch_stream_link("source")
        self.assertEqual(None, url)

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
