from pathlib import Path

from mock import (
    PropertyMock,
    patch,
)
from OpenCast.video import Video

from .util import TestCase


class VideoTest(TestCase):
    def test_construction_from_url(self):
        url = 'https://domain.com/video=test'
        video = Video(url)

        self.assertEqual(video.source, url)
        self.assertIsNone(video.playlist_id)
        self.assertIsNone(video.path)
        self.assertIsNone(video.title)
        self.assertEmpty(video.subtitles)

    def test_construction_from_playlist_url(self):
        url = 'https://domain.com/video=test&playlist=playlist'
        playlist_id = 'id'
        video = Video(url, playlist_id)

        self.assertEqual(video.source, url)
        self.assertEqual(video.playlist_id, playlist_id)
        self.assertIsNone(video.path)
        self.assertIsNone(video.title)
        self.assertEmpty(video.subtitles)

    @patch('OpenCast.video.Path.parent', new_callable=PropertyMock)
    @patch('OpenCast.video.Path.name', new_callable=PropertyMock)
    @patch('OpenCast.video.Path.is_file')
    def test_construction_from_path(self, m_is_file, m_name, m_parent):
        m_is_file.return_value = True
        m_parent.return_value = '/tmp'
        m_name.return_value = 'test'

        path = '/tmp/test'
        video = Video(path)

        self.assertEqual(video.source, path)
        self.assertEqual(video.playlist_id, Path(path).parent)
        self.assertEqual(video.path, path)
        self.assertEqual(video.title, 'test')
        self.assertEmpty(video.subtitles)

    def test_equality(self):
        self.assertEqual(Video('test'), Video('test'))
        self.assertEqual(Video('test', 0), Video('test', 0))
        self.assertNotEqual(Video('test', 0), Video('test', 1))
        self.assertNotEqual(Video('test1', 0), Video('test2', 0))

    @patch('OpenCast.video.Path')
    def test_playlist_id_equality_same_directory(self, path_mock):
        path_mock.is_file.return_value = True

        self.assertEqual(
            Video('/tmp/foo').playlist_id,
            Video('/tmp/bar').playlist_id
        )
