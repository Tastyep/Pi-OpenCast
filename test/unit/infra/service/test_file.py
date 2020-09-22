from test.util import TestCase
from unittest.mock import Mock

from OpenCast.infra.service.file import FileService


class FileServiceTest(TestCase):
    def setUp(self):
        self.service = FileService()

    def test_list_directory(self):
        path = Mock()
        files = [Mock() for i in range(5)]
        expected = []
        for i, file in enumerate(files):
            file.is_file.return_value = i % 2
            if file.is_file():
                expected.append(file)
        path.glob.return_value = files

        self.assertEqual(expected, self.service.list_directory(path, "*"))
        path.glob.assert_called_with("*")
