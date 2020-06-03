from OpenCast.app.command import player as Cmd
from OpenCast.app.controller.player import PlayerController
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.event import player as Evt

from .util import ControllerTestCase


class PlayerControllerTest(ControllerTestCase):
    def setUp(self):
        super(PlayerControllerTest, self).setUp()

        self.data_producer.player().populate(self.data_facade)
        self.controller = PlayerController(self.app_facade, self.data_facade)

    def test_media_end_reached_without_video(self):
        self.raise_event(self.controller, Evt.MediaEndReached, None)
        self.expect_dispatch(Cmd.StopPlayer, IdentityService.id_player())

    def test_media_end_reached_with_videos(self):
        self.data_producer.player().video("source", None).video(
            "next_video", None
        ).populate(self.data_facade)
        self.raise_event(self.controller, Evt.MediaEndReached, None)
        self.expect_dispatch(
            Cmd.PlayVideo,
            IdentityService.id_player(),
            IdentityService.id_video("next_video"),
        )
