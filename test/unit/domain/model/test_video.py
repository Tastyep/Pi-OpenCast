import OpenCast.domain.event.video as Evt
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService

from .util import ModelTestCase


class VideoTest(ModelTestCase):
    def setUp(self):
        self.video = Video(IdentityService.random(), "source")
        self.video.release_events()

    def test_construction(self):
        video = Video(
            IdentityService.random(),
            "source",
            "title",
            "album_name",
            "thumbnail_url",
            "/tmp/file",
            [],
            "subtitle",
        )
        self.assertEqual("source", video.source)
        self.assertEqual("title", video.title)
        self.assertEqual("album_name", video.collection_name)
        self.assertEqual("/tmp/file", video.location)
        self.assertEqual([], video.streams)
        self.assertEqual("subtitle", video.subtitle)
        self.expect_events(video, Evt.VideoCreated)

    def test_retrieve(self):
        self.video.location = "/tmp"
        self.expect_events(self.video, Evt.VideoRetrieved)

    def test_parse(self):
        self.video.streams = {}
        self.expect_events(self.video, Evt.VideoParsed)

    def test_set_subtitles(self):
        self.video.subtitle = "/tmp/toto.srt"
        self.expect_events(self.video, Evt.VideoSubtitleFetched)

    def test_delete(self):
        self.video.delete()
        self.expect_events(self.video, Evt.VideoDeleted)
