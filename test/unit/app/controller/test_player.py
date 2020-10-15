from unittest.mock import Mock

from OpenCast.app.command import player as Cmd
from OpenCast.app.controller.player import PlayerController
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.event import player as Evt

from .util import ControllerTestCase


class PlayerControllerTest(ControllerTestCase):
    def setUp(self):
        super(PlayerControllerTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.service_factory = Mock()
        self.queueing_service = Mock()
        self.service_factory.make_queueing_service.return_value = self.queueing_service
        self.controller = PlayerController(
            self.app_facade, self.data_facade, self.service_factory
        )

    def test_media_end_reached_without_video(self):
        self.queueing_service.next_video.return_value = None
        self.raise_event(self.controller, Evt.MediaEndReached, None)
        self.expect_dispatch(Cmd.StopPlayer, IdentityService.id_player())

    def test_media_end_reached_with_videos(self):
        next_video_id = IdentityService.id_video("source")
        self.queueing_service.next_video.return_value = next_video_id
        self.raise_event(self.controller, Evt.MediaEndReached, None)
        self.expect_dispatch(
            Cmd.PlayVideo,
            IdentityService.id_player(),
            next_video_id,
        )
