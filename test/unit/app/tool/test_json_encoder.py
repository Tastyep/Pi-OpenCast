import json
from enum import Enum
from test.util import TestCase

from OpenCast.app.command.video import CreateVideo
from OpenCast.app.tool.json_encoder import (
    EnhancedJSONEncoder,
    EventEncoder,
    ModelEncoder,
)
from OpenCast.domain.event.video import VideoCreated
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.video import Path, Stream, Video, datetime, timedelta
from OpenCast.domain.service.identity import IdentityService


class EnhancedEncoderTest(TestCase):
    def test_encode_id(self):
        id = IdentityService.random()
        json.dumps({"id": id}, cls=EnhancedJSONEncoder)

    def test_encode_path(self):
        path = Path(".")
        json.dumps({"path": path}, cls=EnhancedJSONEncoder)

    def test_encode_enum(self):
        class Color(Enum):
            RED = 1

        color = Color.RED
        json.dumps({"color": color}, cls=EnhancedJSONEncoder)


class ModelEncoderTest(TestCase):
    def test_encode_player(self):
        player_id = IdentityService.id_player()
        queue_id = IdentityService.id_playlist()
        player = Player(player_id, queue_id)
        json.dumps({"id": IdentityService.random(), "player": player}, cls=ModelEncoder)

    def test_encode_video(self):
        video_id = IdentityService.id_video("source")
        playlist_id = IdentityService.id_playlist()
        video = Video(
            video_id,
            "source",
            playlist_id,
            "album",
            "title",
            timedelta(seconds=300),
            "protocol",
            "thumbnail",
        )
        video.location = "/tmp/video.mp4"
        video.streams = [Stream(0, "audio", "en")]
        video.subtitle = Path("/tmp/video.srt")
        json.dumps({"id": IdentityService.random(), "video": video}, cls=ModelEncoder)


class EventEncoderTest(TestCase):
    def test_encode_event(self):
        video_id = IdentityService.id_video("source")
        collection_id = None
        cmd_id = IdentityService.id_command(CreateVideo, video_id)
        event = VideoCreated(
            cmd_id,
            video_id,
            "source",
            collection_id,
            "album",
            "title",
            300,
            "protocol",
            "thumbnail",
        )
        json.dumps({"id": IdentityService.random(), "event": event}, cls=EventEncoder)
