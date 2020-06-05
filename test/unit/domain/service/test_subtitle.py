from pathlib import Path
from test.util import TestCase
from unittest.mock import MagicMock, Mock

from OpenCast.config import config
from OpenCast.domain.service.subtitle import SubtitleService


class SubtitleServiceTest(TestCase):
    def setUp(self):
        self.downloader = Mock()
        self.service = SubtitleService(self.downloader)

    def test_load_from_disk(self):
        path_mock = MagicMock()
        language = config["subtitle.language"]

        parent_mock = Mock()
        path_mock.parents.__getitem__.return_value = parent_mock
        exp_subtitle = Path("/tmp/source.srt")
        path_mock.with_suffix.return_value = exp_subtitle

        parent_mock.glob.return_value = [exp_subtitle]

        subtitle = self.service.load_from_disk(path_mock, language)
        self.assertEqual(str(exp_subtitle), subtitle)

    def test_download_from_source(self):
        video_source = "http://someurl/id"
        video_path = Mock()
        language = config["subtitle.language"]

        source_subtitle = "/tmp/source.vtt"
        self.downloader.download_subtitle.return_value = source_subtitle

        subtitle = self.service.download_from_source(video_source, video_path, language)
        self.assertEqual(Path(source_subtitle), subtitle)
