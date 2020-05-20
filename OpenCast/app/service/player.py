from functools import partial

import structlog
from OpenCast.app.command import player as player_cmds
from OpenCast.app.error import CommandFailure
from OpenCast.domain.event import player as player_events
from OpenCast.domain.model.player_state import PlayerState
from OpenCast.infra.event import player as infra_events

from .service import Service


class PlayerService(Service):
    def __init__(self, app_facade, data_facade, media_facade):
        logger = structlog.get_logger(__name__)
        super(PlayerService, self).__init__(
            app_facade, logger, self, player_cmds, infra_events
        )

        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo
        self._player = media_facade.player

    # Infra event handler interface implementation

    def _player_stopped(self, evt):
        def stop_player(model):
            model.stop()

        def play_next(model):
            video = model.next_video()
            if video is not None:
                self._player.play(video, model.volume)
                model.play(video)

        self._update(evt.id, stop_player)
        if evt.id is not None:
            return

        self._update(evt.id, play_next)

    # Command handler interface implementation

    def _play_video(self, cmd):
        def queue_video(model, video):
            model.queue(video, with_priority=True)

        video = self._video_repo.get(cmd.video_id)
        self._update(cmd.id, queue_video, video)
        self._play_video_impl(cmd.id, video)

    def _queue_video(self, cmd):
        def queue_video(model):
            video = self._video_repo.get(cmd.video_id)
            model.queue(video)

        self._update(cmd.id, queue_video)

    def _stop_video(self, cmd):
        self._player.stop(cmd.id)
        # Model updates are done from the infra event handler

    def _toggle_video_state(self, cmd):
        def pause(model):
            self._player.pause()
            model.pause()

        def unpause(model):
            self._player.unpause()
            model.unpause()

        model = self._player_model()
        action = pause if model.state is PlayerState.PLAYING else unpause
        self._update(cmd.id, action)

    def _seek_video(self, cmd):
        self._player.seek(cmd.duration)
        # TODO reflect change in model

    def _change_volume(self, cmd):
        def impl(model):
            model.volume = model.volume + cmd.amount
            self._player.set_volume(model.volume)

        self._update(cmd.id, impl)

    def _next_video(self, cmd):
        model = self._player_model()
        next_video = model.next_video()
        if next_video is None:
            raise CommandFailure("no next video")

        self._play_video_impl(cmd.id, next_video)

    def _prev_video(self, cmd):
        model = self._player_model()
        prev_video = model.prev_video()
        if prev_video is None:
            raise CommandFailure("no previous video")

        self._play_video_impl(cmd.id, prev_video)

    def _toggle_subtitle(self, cmd):
        def impl(model, state):
            model.subtitle_state = state

        model = self._player_model()
        state = not model.subtitle_state
        self._player.update_subtitle_state(state)
        self._update(cmd.id, impl, state)

    def _increase_subtitle_delay(self, cmd):
        def impl(model):
            model.subtitle_delay = model.subtitle_delay + cmd.amount

        self._player.increase_subtitle_delay()
        self._update(cmd.id, impl)

    def _decrease_subtitle_delay(self, cmd):
        def impl(model):
            model.subtitle_delay = model.subtitle_delay - cmd.amount

        self._player.increase_subtitle_delay()
        self._update(cmd.id, impl)

    # Private

    def _play_video_impl(self, cmd_id, video):
        def play_video(model, video, *_):
            def impl(model):
                model.play(video)

            self._player.play(video, model.volume)
            self._update(cmd_id, impl)

        model = self._player_model()
        if model.state is not PlayerState.STOPPED:
            callback = partial(play_video, model, video)
            self._evt_dispatcher.once(player_events.PlayerStopped, callback)
            self._player.stop(cmd_id)
        else:
            play_video(model, video)

    def _player_model(self):
        return self._player_repo.get_player()

    def _update(self, cmd_id, mutator, *args):
        def impl(ctx):
            model = self._player_model()
            mutator(model, *args)
            ctx.update(model)

        self._start_transaction(self._player_repo, cmd_id, impl)
