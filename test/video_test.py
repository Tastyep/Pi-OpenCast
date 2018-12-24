from pathlib import Path

from RaspberryCast.video import Video

from .util import TestCase


class VideoTest(TestCase):
    def make_file(self, file):
        Path(file).touch()

    def test_construction_from_url(self):
        url = 'https://domain.com/video=test'
        video = Video(url)

        self.assertEqual(video.url, url)
        self.assertIsNone(video.playlist_id)
        self.assertIsNone(video.path)
        self.assertIsNone(video.title)
        self.assertEmpty(video.subtitles)

    def test_construction_from_playlist_url(self):
        url = 'https://domain.com/video=test&playlist=playlist'
        playlist_id = 'id'
        video = Video(url, playlist_id)

        self.assertEqual(video.url, url)
        self.assertEqual(video.playlist_id, playlist_id)
        self.assertIsNone(video.path)
        self.assertIsNone(video.title)
        self.assertEmpty(video.subtitles)

    def test_construction_from_path(self):
        path = '/tmp/test'
        video = Video(path)

        self.make_file(path)

        self.assertEqual(video.url, path)
        self.assertEqual(video.playlist_id, Path(path).parent)
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

        self.assertEqual(Video('/tmp/foo').playlist_id,
                         Video('/tmp/bar').playlist_id)
