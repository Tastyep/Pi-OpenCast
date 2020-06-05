import OpenCast.domain.event.video as Evt
from OpenCast.domain.model.video import Video

from .util import ModelTestCase


class VideoTest(ModelTestCase):
    def test_construction(self):
        video = Video(None, "source", None)
        self.assertEqual(None, video.playlist_id)
        self.assertEqual("source", video.source)
        self.assertEqual(None, video.title)
        self.assertEqual(None, video.path)
        self.assertEqual([], video.streams)
        self.assertEqual(None, video.subtitle)
        self.expect_events(video, Evt.VideoCreated)

    def make_video(self):
        video = Video(None, "source", None)
        # Pop the VideoCreatedEvent
        video.release_events()
        return video

    def test_identify(self):
        video = self.make_video()
        video.title = "name"
        self.expect_events(video, Evt.VideoIdentified)

    def test_retrieve(self):
        video = self.make_video()
        video.path = "/tmp"
        self.expect_events(video, Evt.VideoRetrieved)

    def test_parse(self):
        video = self.make_video()
        video.streams = {}
        self.expect_events(video, Evt.VideoParsed)

    def test_set_subtitles(self):
        video = self.make_video()
        video.subtitle = "/tmp/toto.srt"
        self.expect_events(video, Evt.VideoSubtitleFetched)

    def test_delete(self):
        video = self.make_video()
        video.delete()
        self.expect_events(video, Evt.VideoDeleted)
