import json
from test.util import TestCase

from OpenCast.app.command.video import CreateVideo
from OpenCast.app.tool.json_encoder import EventEncoder, ModelEncoder
from OpenCast.domain.event.video import VideoCreated
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.video import Path, Stream, Video
from OpenCast.domain.service.identity import IdentityService


class ModelEncoderTest(TestCase):
    def test_encode_player(self):
        player_id = IdentityService.id_player()
        queue_id = IdentityService.id_playlist()
        player = Player(player_id, queue_id)
        json.dumps({"id": IdentityService.random(), "player": player}, cls=ModelEncoder)

    def test_encode_video(self):
        video_id = IdentityService.id_video("source")
        video = Video(video_id, "source", "title", "album", "thumbnail")
        video.path = Path("/tmp/video.mp4")
        video.streams = [Stream(0, "audio", "en")]
        video.subtitle = Path("/tmp/video.srt")
        json.dumps({"id": IdentityService.random(), "video": video}, cls=ModelEncoder)


class EventEncoderTest(TestCase):
    def test_encode_event(self):
        video_id = IdentityService.id_video("source")
        cmd_id = IdentityService.id_command(CreateVideo, video_id)
        event = VideoCreated(cmd_id, video_id, "source", "title", "album", "thumbnail")
        json.dumps({"id": IdentityService.random(), "event": event}, cls=EventEncoder)
