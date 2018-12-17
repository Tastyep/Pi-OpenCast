from .util import TestCase

from RaspberryCast.video import Video
from pathlib import Path


class VideoTest(TestCase):
    def make_file(self, file):
        Path(file).touch()

    def test_construction_from_url(self):
        url = 'https://domain.com/video=test'
        video = Video(url)

        self.assertEqual(video.url, url)
        self.assertIsNone(video.playlistId)
        self.assertIsNone(video.path)
        self.assertIsNone(video.title)
        self.assertEmpty(video.subtitles)

    def test_construction_from_playlist_url(self):
        url = 'https://domain.com/video=test&playlist=playlist'
        playlistId = 'id'
        video = Video(url, playlistId)

        self.assertEqual(video.url, url)
        self.assertEqual(video.playlistId, playlistId)
        self.assertIsNone(video.path)
        self.assertIsNone(video.title)
        self.assertEmpty(video.subtitles)

    def test_construction_from_path(self):
        path = '/tmp/test'
        video = Video(path)

        self.make_file(path)

        self.assertEqual(video.url, path)
        self.assertEqual(video.playlistId, Path(path).parent)
        self.assertEqual(video.path, Path(path))
        self.assertEqual(video.title, 'test')
        self.assertEmpty(video.subtitles)

    def test_equality(self):
        self.assertEqual(Video('test'), Video('test'))
        self.assertEqual(Video('test', 0), Video('test', 0))
        self.assertNotEqual(Video('test', 0), Video('test', 1))

    def test_local_video_same_parent(self):
        self.make_file('/tmp/foo')
        self.make_file('/tmp/bar')

        self.assertEqual(Video('/tmp/foo').playlistId,
                         Video('/tmp/bar').playlistId)
