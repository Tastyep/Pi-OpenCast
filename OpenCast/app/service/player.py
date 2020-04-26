import logging
from functools import partial

from OpenCast.app.command import player as player_cmds
from OpenCast.app.error import CommandFailure
from OpenCast.domain.event import player as player_events
from OpenCast.domain.model.player_state import PlayerState
from OpenCast.infra.event import player as infra_events

from .service import Service


class PlayerService(Service):
    def __init__(self, app_facade, data_facade, media_facade):
        logger = logging.getLogger(__name__)
        super(PlayerService, self).__init__(
            app_facade, logger, self, player_cmds, infra_events
        )

        self._player_repo = data_facade.player_repo()
        self._video_repo = data_facade.video_repo()
        self._player = media_facade.player()

    # Infra event handler interface implementation

    def _player_started(self, evt):
        def impl(model):
            model.play(evt.video)

        self._update(evt.id, impl)

    def _player_stopped(self, evt):
        def stop_player(model):
            model.stop()

        self._update(evt.id, stop_player)
        if evt.id is not None:
            return

        model = self._player_model()
        video = model.next_video()
        if video is not None:
            self._player.play(evt.id, video, model.volume)

    def _player_paused(self, evt):
        def impl(model):
            model.pause()

        self._update(evt.id, impl)

    def _player_unpaused(self, evt):
        def impl(model):
            model.unpause()

        self._update(evt.id, impl)

    def _video_seeked(self, evt):
        pass

    def _subtitle_delay_updated(self, evt):
        def impl(model):
            model.subtitle_delay = model.subtitle_delay + evt.amount

        self._update(evt.id, impl)

    def _volume_updated(self, evt):
        def impl(model):
            model.volume = evt.volume

        self._update(evt.id, impl)

    def _subtitle_state_changed(self, evt):
        def impl(model):
            model.subtitle_state = evt.state

        self._update(evt.id, impl)

    # Command handler interface implementation

    def _play_video(self, cmd):
        def queue_video(model, video):
            model.queue(video, with_priority=True)

        video = self._video_repo.get(cmd.video_id)
        self._update(cmd.id, queue_video, video)

        def play_video(video, *_):
            model = self._player_model()
            self._player.play(cmd.id, video, model.volume)

        model = self._player_model()
        if model.state != PlayerState.STOPPED:
            callback = partial(play_video, video)
            # TODO: Should be model events
            self._evt_dispatcher.once(player_events.PlayerStopped, callback)
            self._player.stop(cmd.id)
        else:
            play_video(video)

    def _queue_video(self, cmd):
        def queue_video(model):
            video = self._video_repo.get(cmd.video_id)
            model.queue(video)

        self._update(cmd.id, queue_video)

    def _stop_video(self, cmd):
        self._player.stop(cmd.id)

    def _toggle_video_state(self, cmd):
        player_model = self._player_model()
        if player_model.state is PlayerState.PLAYING:
            self._player.pause(cmd.id)
        else:
            self._player.unpause(cmd.id)

    def _seek_video(self, cmd):
        self._player.seek(cmd.id, cmd.duration)

    def _change_volume(self, cmd):
        model = self._player_model()
        model.volume = model.volume + cmd.amount
        self._player.set_volume(cmd.id, model.volume)

    def _next_video(self, cmd):
        model = self._player_model()
        video = model.next_video()
        if video is None:
            raise CommandFailure("no next video")

        def play_next(video, *_):
            model = self._player_model()
            self._player.play(cmd.id, video, model.volume)

        if model.state != PlayerState.STOPPED:
            callback = partial(play_next, video)
            self._evt_dispatcher.once(player_events.PlayerStopped, callback)
            self._player.stop(cmd.id)
        else:
            play_next(video)

    def _prev_video(self, cmd):
        model = self._player_model()
        video = model.prev_video()
        if video is None:
            raise CommandFailure("no previous video")

        def play_prev(video, *_):
            model = self._player_model()
            self._player.play(cmd.id, video, model.volume)

        if model.state is not PlayerState.STOPPED:
            callback = partial(play_prev, video)
            self._evt_dispatcher.once(player_events.PlayerStopped, callback)
            self._player.stop(cmd.id)
        else:
            play_prev(video)

    def _toggle_subtitle(self, cmd):
        state = not self._player_model().subtitle_state
        self._player.update_subtitle_state(cmd.id, state)

    def _increase_subtitle_delay(self, cmd):
        self._player.increase_subtitle_delay(cmd.id)

    def _decrease_subtitle_delay(self, cmd):
        self._player.increase_subtitle_delay(cmd.id)

    # Private

    def _player_model(self):
        return self._player_repo.get_player()

    def _update(self, cmd_id, mutator, *args):
        def impl(ctx):
            model = self._player_model()
            mutator(model, *args)
            ctx.update(model)

        self._start_transaction(self._player_repo, cmd_id, impl)
