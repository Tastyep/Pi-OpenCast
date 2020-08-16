import json
from test.util import TestCase

from OpenCast.app.tool.json_encoder import ModelEncoder
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.video import Path, Stream, Video
from OpenCast.domain.service.identity import IdentityService


class JsonEncoderTest(TestCase):
    def test_encode_player(self):
        player_id = IdentityService.id_player()
        player = Player(player_id)
        json.dumps(player, cls=ModelEncoder)

    def test_encode_video(self):
        video_id = IdentityService.id_video("source")
        video = Video(video_id, "source", None)
        video.metadata = {"title": "title", "thumbnail": "thumbnail_url"}
        video.path = Path("/tmp/video.mp4")
        video.streams = [Stream(0, "audio", "en")]
        video.subtitle = Path("/tmp/video.srt")
        json.dumps(video, cls=ModelEncoder)
