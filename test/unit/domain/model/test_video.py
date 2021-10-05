import OpenCast.domain.event.video as Evt
from OpenCast.domain.error import DomainError
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.model.video import Video, timedelta
from OpenCast.domain.service.identity import IdentityService

from .util import ModelTestCase


class VideoTest(ModelTestCase):
    def setUp(self):
        self.video = Video(IdentityService.random(), "source")
        self.video.release_events()

    def test_construction(self):
        collection_id = IdentityService.random()
        video = Video(
            IdentityService.random(),
            "source",
            collection_id,
            "album_name",
            "title",
            timedelta(seconds=300),
            timedelta(),
            None,
            "protocol",
            "thumbnail_url",
            "/tmp/file",
            [],
            "subtitle",
        )
        self.assertEqual("source", video.source)
        self.assertEqual(collection_id, video.collection_id)
        self.assertEqual("album_name", video.collection_name)
        self.assertEqual("title", video.title)
        self.assertEqual(300, video.duration)
        self.assertEqual("/tmp/file", video.location)
        self.assertEqual([], video.streams)
        self.assertEqual("subtitle", video.subtitle)
        self.expect_events(video, Evt.VideoCreated)

    def test_retrieve(self):
        self.video.location = "/tmp"
        self.expect_events(self.video, Evt.VideoRetrieved)

    def test_parse(self):
        self.video.streams = {}
        self.expect_events(self.video, Evt.VideoParsed, Evt.VideoStateUpdated)

    def test_set_subtitles(self):
        self.video.subtitle = "/tmp/toto.srt"
        self.expect_events(self.video, Evt.VideoSubtitleFetched)

    def test_streamable(self):
        self.assertFalse(self.video.streamable())
        video = Video(IdentityService.random(), "source", source_protocol="m3u8")
        self.assertTrue(video.streamable())

    def test_start(self):
        self.video.state = VideoState.READY
        self.video.release_events()

        self.video.start()
        self.expect_events(self.video, Evt.VideoStateUpdated)

    def test_start_not_ready(self):
        with self.assertRaises(DomainError) as ctx:
            self.video.start()
        self.assertEqual("the video can't be started", str(ctx.exception))

    def test_start_stop(self):
        self.video.state = VideoState.READY
        self.video.release_events()

        self.video.start()
        self.video.stop()
        self.expect_events(self.video, Evt.VideoStateUpdated, Evt.VideoStateUpdated)

    def test_stop_not_started(self):
        with self.assertRaises(DomainError) as ctx:
            self.video.stop()
        self.assertEqual("the video is not playing", str(ctx.exception))

    def test_delete(self):
        self.video.delete()
        self.expect_events(self.video, Evt.VideoDeleted)
