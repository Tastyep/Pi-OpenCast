from test.util import TestCase

from OpenCast.domain.service.subtitle import SubtitleService


class SubtitleServiceTest(TestCase):
    def setUp(self):
        self._service = SubtitleService(None, None)

    def test_load_from_disk(self):
        pass
