from OpenCast.config import (
    Downloader,
    Server,
    VideoPlayer,
    config,
)

from .util import TestCase


class ConfigTest(TestCase):
    def test_categories(self):
        self.assertIsInstance(config['Server'], Server)
        self.assertIsInstance(config['VideoPlayer'], VideoPlayer)
        self.assertIsInstance(config['Downloader'], Downloader)

    def test_default_values(self):
        vp = config['VideoPlayer']
        self.assertTrue(vp.hide_background)
        self.assertEqual(vp.history_size, 15)

        dl = config['Downloader']
        self.assertEqual(dl.output_directory, '/tmp')

    def test_parse_video_player_config(self):
        config.load_from_dict({
            'VideoPlayer': {
                'hide_background': False,
                'history_size': 10
            }
        })

        vp = config['VideoPlayer']
        self.assertFalse(vp.hide_background)
        self.assertEqual(vp.history_size, 10)

    def test_parse_downloader_config(self):
        config.load_from_dict({
            'Downloader': {
                'output_directory': '/Video'
            }
        })

        dl = config['Downloader']
        self.assertEqual(dl.output_directory, '/Video')

    def test_parse_server_config(self):
        config.load_from_dict({
            'Server': {
                'host': 'host',
                'port': 42
            }
        })

        sv = config['Server']
        self.assertEqual(sv.host, 'host')
        self.assertEqual(sv.port, 42)

    def test_parse_quoted_string(self):
        config.load_from_dict({
            'Server': {
                'host': '"host"',
            }
        })

        sv = config['Server']
        self.assertEqual(sv.host, 'host')
