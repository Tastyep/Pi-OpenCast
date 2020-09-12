from pathlib import Path
from test.util import TestCase
from unittest.mock import MagicMock, Mock

from OpenCast.config import config
from OpenCast.domain.service.subtitle import SubtitleService


class SubtitleServiceTest(TestCase):
    def setUp(self):
        self.downloader = Mock()
        self.lang = config["subtitle.language"]

        self.video = Mock()
        path_mock = MagicMock()
        self.video.path = path_mock

        self.service = SubtitleService(self.downloader)

    def expect_from_disk(self, files):
        parent_mock = Mock()
        self.video.path.parents.__getitem__.return_value = parent_mock
        self.video.path.with_suffix.return_value = Path("/tmp/video.srt")
        parent_mock.glob.return_value = [Path(file) for file in files]

    def expect_from_source(self, file):
        self.video.from_disk.return_value = False
        self.downloader.download_subtitle.return_value = file

    def test_load_from_disk(self):
        found_sub = "/tmp/video.srt"
        self.expect_from_disk([found_sub])

        subtitle = self.service.fetch_subtitle(self.video, self.lang)
        self.assertEqual(found_sub, subtitle)

    def test_download_from_source(self):
        self.expect_from_disk([])

        source_subtitle = "/tmp/source.vtt"
        self.expect_from_source(source_subtitle)

        subtitle = self.service.fetch_subtitle(self.video, self.lang)
        self.assertEqual(Path(source_subtitle), subtitle)

    def test_fetch_online(self):
        self.expect_from_disk([])
        self.expect_from_source(None)
        subtitle = self.service.fetch_subtitle(self.video, self.lang)
        self.assertEqual(None, subtitle)
