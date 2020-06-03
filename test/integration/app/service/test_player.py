from unittest.mock import Mock

from OpenCast.app.command import player as Cmd
from OpenCast.app.service.player import PlayerService
from OpenCast.domain.event import player as Evt
from OpenCast.domain.model.player import Player
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class PlayerServiceTest(ServiceTestCase):
    def setUp(self):
        super(PlayerServiceTest, self).setUp()

        self.player = Mock()
        media_factory = self.infra_facade.media_factory
        media_factory.make_player = Mock(return_value=self.player)

        self.service = PlayerService(self.app_facade, self.data_facade, media_factory)

        self.player_repo = self.data_facade.player_repo
        self.video_repo = self.data_facade.video_repo

        self.player_id = IdentityService.id_player()
        self.data_producer.player().populate(self.data_facade)

    def test_play_video(self):
        self.data_producer.video("source", None).populate(self.data_facade)

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoQueued, video_id).expect(
            Evt.PlayerStarted, video_id
        ).from_(Cmd.PlayVideo, self.player_id, video_id)

    def test_queue_video(self):
        self.data_producer.video("source", None).populate(self.data_facade)

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.VideoQueued, video_id).from_(
            Cmd.QueueVideo, self.player_id, video_id
        )

    def test_stop_video(self):
        self.data_producer.player().video("source", None).play().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.PlayerStopped).from_(Cmd.StopVideo, self.player_id)

    def test_pause_video(self):
        self.data_producer.player().video("source", None).play().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.PlayerPaused).from_(
            Cmd.ToggleVideoState, self.player_id
        )

    def test_unpause_video(self):
        self.data_producer.player().video("source", None).play().pause().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.PlayerUnpaused).from_(
            Cmd.ToggleVideoState, self.player_id
        )

    def test_change_video_volume(self):
        self.data_producer.player().video("source", None).play().populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.VolumeUpdated).from_(
            Cmd.ChangeVolume, self.player_id, Player.VOLUME_STEP
        )

    def test_next_video(self):
        self.data_producer.player().video("source", None).play().video(
            "source2", None
        ).populate(self.data_facade)

        next_video_id = IdentityService.id_video("source2")
        self.evt_expecter.expect(Evt.PlayerStarted, next_video_id).from_(
            Cmd.NextVideo, self.player_id
        )

    def test_prev_video(self):
        self.data_producer.player().video("source", None).video(
            "source2", None
        ).play().populate(self.data_facade)

        prev_video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(Evt.PlayerStarted, prev_video_id).from_(
            Cmd.PrevVideo, self.player_id
        )

    def test_toggle_subtitle(self):
        self.data_producer.player().populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleStateUpdated).from_(
            Cmd.ToggleSubtitle, self.player_id
        )

    def test_increase_subtitle_delay(self):
        self.data_producer.player().populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleDelayUpdated).from_(
            Cmd.IncreaseSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP
        )

    def test_decrease_subtitle_delay(self):
        self.data_producer.player().populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleDelayUpdated).from_(
            Cmd.DecreaseSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP
        )
