from collections import namedtuple
from test.util import TestCase
from unittest.mock import Mock

from OpenCast.infra.media.parser import VideoParser, VideoParsingError
from vlc import MediaParsedStatus, TrackType

Stream = namedtuple("Stream", ["id", "type", "language"])


class VideoParserTest(TestCase):
    def setUp(self):
        self.vlc = Mock()
        self.parser = VideoParser(self.vlc)

    def test_parse_streams(self):
        video_path = "/tmp/source.mp4"
        media = Mock()
        self.vlc.media_new.return_value = media
        media.parse_with_options.return_value = 0
        media.get_parsed_status.return_value = MediaParsedStatus.done
        media.is_parsed.return_value = 1

        input_languages = [b"eng", None, b"\xE2\x82\xAC"]
        output_languages = ["eng", None, "€"]
        input_types = [TrackType.audio, TrackType.video, TrackType.ext]
        output_types = ["audio", "video", "subtitle"]

        streams = [(i, input_types[i], input_languages[i]) for i in range(3)]
        expected = [(i, output_types[i], output_languages[i]) for i in range(3)]

        media.tracks_get.return_value = [Stream(*stream) for stream in streams]
        self.assertEqual(expected, self.parser.parse_streams(video_path))

    def test_parse_streams_failed(self):
        video_path = "/tmp/source.mp4"
        media = Mock()
        self.vlc.media_new.return_value = media
        status = MediaParsedStatus.failed
        media.get_parsed_status.return_value = status
        media.parse_with_options.return_value = -1
        with self.assertRaises(VideoParsingError) as ctx:
            self.parser.parse_streams(video_path)
        self.assertEqual(
            f"Can't parse streams from '{video_path}', status='{status}'",
            str(ctx.exception),
        )

    def test_parse_streams_timeout(self):
        video_path = "/tmp/source.mp4"
        media = Mock()
        self.vlc.media_new.return_value = media
        status = MediaParsedStatus.timeout
        media.get_parsed_status.return_value = status
        media.parse_with_options.return_value = 0
        with self.assertRaises(VideoParsingError) as ctx:
            self.parser.parse_streams(video_path)
        self.assertEqual(
            f"Can't parse streams from '{video_path}', status='{status}'",
            str(ctx.exception),
        )
