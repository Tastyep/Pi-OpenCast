from test.util import TestCase

import OpenCast.domain.event.video as Evt
from OpenCast.domain.model.video import Video


class VideoTest(TestCase):
    def test_construction(self):
        video = Video(None, "source", None)
        self.assertEqual(None, video.playlist_id)
        self.assertEqual("source", video.source)
        self.assertEqual(None, video.title)
        self.assertEqual(None, video.path)
        self.assertEqual(None, video.subtitle)

        video_evts = video.release_events()
        self.assertListEqual([Evt.VideoCreated], video_evts.keys())

    def make_video(self):
        video = Video(None, "source", None)
        # Pop the VideoCreatedEvent
        video.release_events()
        return video

    def test_identify(self):
        video = self.make_video()
        video.title = "name"
        self.assertListEqual([Evt.VideoIdentified], video.release_events().keys())

    def test_retrieve(self):
        video = self.make_video()
        video.path = "/tmp"
        self.assertListEqual([Evt.VideoRetrieved], video.release_events().keys())

    def test_set_subtitles(self):
        video = self.make_video()
        video.subtitle = "/tmp/toto.srt"
        self.assertListEqual([Evt.VideoSubtitleFetched], video.release_events().keys())

    def test_delete(self):
        video = self.make_video()
        video.delete()
        self.assertListEqual([Evt.VideoDeleted], video.release_events().keys())
