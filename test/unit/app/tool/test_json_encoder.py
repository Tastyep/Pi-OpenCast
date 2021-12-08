import json
from datetime import datetime, timedelta
from enum import Enum
from test.util import TestCase

from OpenCast.app.command.video import CreateVideo
from OpenCast.app.notification import Level as NotifLevel
from OpenCast.app.notification import Notification
from OpenCast.app.tool.json_encoder import (
    EnhancedJSONEncoder,
    EventEncoder,
    ModelEncoder,
)
from OpenCast.domain.event.video import VideoCreated
from OpenCast.domain.model.album import Album
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.playlist import Playlist
from OpenCast.domain.model.video import Path
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.model.video import Stream, Video
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.event.downloader import DownloadInfo


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

    def test_encode_datetime(self):
        now = datetime.now()
        json.dumps({"now": now}, cls=EnhancedJSONEncoder)

    def test_encode_timedelta(self):
        duration = timedelta()
        json.dumps({"duration": duration}, cls=EnhancedJSONEncoder)


class ModelEncoderTest(TestCase):
    def test_encode_player(self):
        player_id = IdentityService.id_player()
        queue_id = IdentityService.id_playlist()
        player = Player(player_id, queue_id)
        json.dumps(player, cls=ModelEncoder)

    def test_encode_video(self):
        video_id = IdentityService.id_video("source")
        playlist_id = IdentityService.id_playlist()
        video = Video(
            video_id,
            "source",
            playlist_id,
            "artist",
            "album",
            "title",
            timedelta(seconds=300),
            timedelta(minutes=10),
            datetime(2020, 10, 5),
            "protocol",
            "thumbnail",
        )
        video.location = "/tmp/video.mp4"
        video.streams = [Stream(0, "audio", "en")]
        video.subtitle = Path("/tmp/video.srt")
        json.dumps(video, cls=ModelEncoder)

    def test_encode_playlist(self):
        playlist_id = IdentityService.id_playlist()
        playlist = Playlist(
            playlist_id, "title", [IdentityService.random()], generated=True
        )
        json.dumps(playlist, cls=ModelEncoder)

    def test_encode_album(self):
        name = "name"
        album_id = IdentityService.id_album(name)
        album = Album(album_id, name, [IdentityService.random()], "thumbnail")
        json.dumps(album, cls=ModelEncoder)


class EventEncoderTest(TestCase):
    def test_encode_app_notification(self):
        notif = Notification(IdentityService.random(), NotifLevel.INFO, "message")
        json.dumps(notif, cls=EventEncoder)

    def test_encode_domain_event(self):
        video_id = IdentityService.id_video("source")
        collection_id = None
        cmd_id = IdentityService.id_command(CreateVideo, video_id)
        event = VideoCreated(
            cmd_id,
            video_id,
            "source",
            collection_id,
            IdentityService.id_artist("artist"),
            IdentityService.id_album("album"),
            "title",
            300,
            "protocol",
            "thumbnail",
            VideoState.CREATED,
        )
        json.dumps(event, cls=EventEncoder)

    def test_encode_infra_event(self):
        event = DownloadInfo(IdentityService.random(), IdentityService.random(), 0, 0)
        json.dumps(event, cls=EventEncoder)
