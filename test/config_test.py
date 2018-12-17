from .util import TestCase

from RaspberryCast.config import (
    VideoPlayer,
    Downloader,
    config,
)


class ConfigTest(TestCase):
    def test_categories(self):
        self.assertIsInstance(config['VideoPlayer'], VideoPlayer)
        self.assertIsInstance(config['Downloader'], Downloader)

    def test_default_values(self):
        vp = config['VideoPlayer']
        self.assertTrue(vp.hide_background)
        self.assertEqual(15, vp.history_size)

        dl = config['Downloader']
        self.assertEqual('/tmp', dl.output_directory)

    def test_parse_video_player_config(self):
        config.load_from_dict({
            'VideoPlayer': {
                'hide_background': False,
                'history_size': 10
            }
        })

        vp = config['VideoPlayer']
        self.assertFalse(vp.hide_background)
        self.assertEqual(10, vp.history_size)

    def test_parse_downloader_config(self):
        config.load_from_dict({
            'Downloader': {
                'output_directory': '/Video'
            }
        })

        dl = config['Downloader']
        self.assertEqual('/Video', dl.output_directory)
