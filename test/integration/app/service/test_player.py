from OpenCast.app.command import player as Cmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.event import player as Evt
from OpenCast.domain.model.player import Player
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class PlayerServiceTest(ServiceTestCase):
    def setUp(self):
        super(PlayerServiceTest, self).setUp()

        self.video_repo = self.data_facade.video_repo

        self.player_id = IdentityService.id_player()

    def test_play_video(self):
        self.data_producer.player().video("source", None).video(
            "source2", None
        ).populate(self.data_facade)

        video_id = IdentityService.id_video("source2")
        self.evt_expecter.expect(Evt.PlayerStarted, self.player_id, video_id).from_(
            Cmd.PlayVideo, self.player_id, video_id
        )

    def test_play_video_not_queued(self):
        self.data_producer.video("source", None).player().video(
            "source2", None
        ).populate(self.data_facade)

        video_id = IdentityService.id_video("source")
        video = self.video_repo.get(video_id)
        self.evt_expecter.expect(OperationError, f"unknown video: {video}").from_(
            Cmd.PlayVideo, self.player_id, video_id
        )

    def test_queue_video(self):
        self.data_producer.video("source", None).populate(self.data_facade)

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoQueued, self.player_id, video_id).from_(
            Cmd.QueueVideo, self.player_id, video_id
        )

    def test_stop_player(self):
        self.data_producer.player().video("source", None).play().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.PlayerStopped, self.player_id).from_(
            Cmd.StopPlayer, self.player_id
        )

    def test_toggle_player_state(self):
        self.data_producer.player().video("source", None).play().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.PlayerStateToggled, self.player_id).from_(
            Cmd.TogglePlayerState, self.player_id
        )

    def test_change_video_volume(self):
        self.data_producer.player().video("source", None).play().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.VolumeUpdated, self.player_id, 80).from_(
            Cmd.UpdateVolume, self.player_id, 80
        )

    def test_toggle_subtitle(self):
        self.data_producer.populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleStateUpdated, self.player_id).from_(
            Cmd.ToggleSubtitle, self.player_id
        )

    def test_increase_subtitle_delay(self):
        self.data_producer.populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleDelayUpdated, self.player_id).from_(
            Cmd.AdjustSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP
        )

    def test_decrease_subtitle_delay(self):
        self.data_producer.populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleDelayUpdated, self.player_id).from_(
            Cmd.DecreaseSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP
        )
