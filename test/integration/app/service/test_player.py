from datetime import datetime, timedelta
from unittest.mock import patch

from OpenCast.app.command import player as Cmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.event import player as Evt
from OpenCast.domain.event import video as VideoEvt
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.player import State as PlayerState
from OpenCast.domain.model.video import State as VideoState
from OpenCast.domain.service.identity import IdentityService

from .util import ServiceTestCase


class PlayerServiceTest(ServiceTestCase):
    def setUp(self):
        super(PlayerServiceTest, self).setUp()

        self.video_repo = self.data_facade.video_repo

        self.player_id = IdentityService.id_player()
        self.player_playlist_id = HOME_PLAYLIST.id

    def test_create(self):
        self.evt_expecter.expect(
            Evt.PlayerCreated,
            self.player_id,
            self.player_playlist_id,
            PlayerState.STOPPED,
            True,
            0,
            70,
        ).from_(Cmd.CreatePlayer, self.player_id, self.player_playlist_id)
        self.media_player.set_volume.assert_called_once_with(70)

    @patch("OpenCast.domain.model.video.datetime")
    def test_play_video(self, datetime_mock):
        now = datetime.now()
        datetime_mock.now.return_value = now

        self.data_producer.player().video("source", state=VideoState.READY).populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(
            Evt.PlayerStateUpdated,
            self.player_id,
            PlayerState.STOPPED,
            PlayerState.PLAYING,
            video_id,
        ).expect(
            VideoEvt.VideoStateUpdated,
            video_id,
            VideoState.READY,
            VideoState.PLAYING,
            timedelta(),
            now,
        ).from_(
            Cmd.PlayVideo, self.player_id, video_id
        )

    @patch("OpenCast.domain.model.video.datetime")
    def test_stop_player(self, datetime_mock):
        now = datetime.now()
        datetime_mock.now.return_value = now

        self.data_producer.player().video("source").play("source").populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(
            Evt.PlayerStateUpdated,
            self.player_id,
            PlayerState.PLAYING,
            PlayerState.STOPPED,
            video_id,
        ).expect(
            VideoEvt.VideoStateUpdated,
            video_id,
            VideoState.PLAYING,
            VideoState.READY,
            timedelta(),
            now,
        ).from_(
            Cmd.StopPlayer, self.player_id
        )

    @patch("OpenCast.domain.model.video.datetime")
    def test_toggle_player_state(self, datetime_mock):
        now = datetime.now()
        datetime_mock.now.return_value = now

        self.data_producer.player().video("source").play("source").populate(
            self.data_facade
        )

        video_id = IdentityService.id_video("source")
        self.evt_expecter.expect(
            Evt.PlayerStateUpdated,
            self.player_id,
            PlayerState.PLAYING,
            PlayerState.PAUSED,
            video_id,
        ).expect(
            VideoEvt.VideoStateUpdated,
            video_id,
            VideoState.PLAYING,
            VideoState.READY,  #
            timedelta(),
            now,
        ).from_(
            Cmd.TogglePlayerState, self.player_id
        )
        self.evt_expecter.expect(
            Evt.PlayerStateUpdated,
            self.player_id,
            PlayerState.PAUSED,
            PlayerState.PLAYING,
            video_id,
        ).expect(
            VideoEvt.VideoStateUpdated,
            video_id,
            VideoState.READY,
            VideoState.PLAYING,  #
            timedelta(),
            now,
        ).from_(
            Cmd.TogglePlayerState, self.player_id
        )

    def test_seek_video(self):
        self.data_producer.player().video("source").play("source").populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.VideoSeeked, self.player_id).from_(
            Cmd.SeekVideo, self.player_id, 1
        )

    def test_seek_video_not_started(self):
        self.data_producer.player().video("source").populate(self.data_facade)

        self.evt_expecter.expect(OperationError, "the player is not started").from_(
            Cmd.SeekVideo, self.player_id, 1
        )

    def test_change_video_volume(self):
        self.data_producer.player().video("source").play("source").populate(
            self.data_facade
        )

        self.evt_expecter.expect(Evt.VolumeUpdated, self.player_id, 80).from_(
            Cmd.UpdateVolume, self.player_id, 80
        )

    def test_toggle_subtitle(self):
        self.data_producer.player().populate(self.data_facade)

        self.evt_expecter.expect(Evt.SubtitleStateUpdated, self.player_id, False).from_(
            Cmd.ToggleSubtitle, self.player_id
        )
        self.evt_expecter.expect(Evt.SubtitleStateUpdated, self.player_id, True).from_(
            Cmd.ToggleSubtitle, self.player_id
        )

    def test_increase_subtitle_delay(self):
        self.data_producer.player().populate(self.data_facade)

        self.evt_expecter.expect(
            Evt.SubtitleDelayUpdated, self.player_id, Player.SUBTITLE_DELAY_STEP
        ).from_(Cmd.AdjustSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP)

    def test_decrease_subtitle_delay(self):
        self.data_producer.player().populate(self.data_facade)

        self.evt_expecter.expect(
            Evt.SubtitleDelayUpdated, self.player_id, -Player.SUBTITLE_DELAY_STEP
        ).from_(Cmd.DecreaseSubtitleDelay, self.player_id, Player.SUBTITLE_DELAY_STEP)
