import structlog
from OpenCast.app.command import player as player_cmds
from OpenCast.config import config
from OpenCast.domain.model.player import State as PlayerState

from .service import Service


class PlayerService(Service):
    def __init__(self, app_facade, data_facade, media_factory):
        logger = structlog.get_logger(__name__)
        super().__init__(app_facade, logger, self, player_cmds)

        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo
        self._player = media_factory.make_player(app_facade.evt_dispatcher)

        model = self._player_model()
        self._player.set_volume(model.volume)

    # Command handler interface implementation

    def _play_video(self, cmd):
        video = self._video_repo.get(cmd.video_id)
        self._queue_video_impl(cmd.id, video)
        self._play_video_impl(cmd.id, video)

    def _queue_video(self, cmd):
        video = self._video_repo.get(cmd.video_id)
        self._queue_video_impl(cmd.id, video)

    def _stop_player(self, cmd):
        def stop_video(model):
            model.stop()
            self._player.stop()

        self._update(cmd.id, stop_video)

    def _toggle_player_state(self, cmd):
        def toggle_state(model):
            model.toggle_pause()
            if model.state is PlayerState.PAUSED:
                self._player.pause()
            else:
                self._player.unpause()

        self._update(cmd.id, toggle_state)

    def _seek_video(self, cmd):
        self._player.seek(cmd.duration)
        # TODO reflect change in model

    def _change_volume(self, cmd):
        def impl(model):
            model.volume = cmd.volume
            self._player.set_volume(model.volume)

        self._update(cmd.id, impl)

    def _pick_video(self, cmd):
        model = self._player_model()
        video = model.pick(cmd.video_id)
        self._play_video_impl(cmd.id, video)

    def _toggle_subtitle(self, cmd):
        def impl(model):
            model.subtitle_state = not model.subtitle_state

        self._player.toggle_subtitle()
        self._update(cmd.id, impl)

    def _increase_subtitle_delay(self, cmd):
        def impl(model):
            model.subtitle_delay = model.subtitle_delay + cmd.amount
            self._player.set_subtitle_delay(model.subtitle_delay)

        self._update(cmd.id, impl)

    def _decrease_subtitle_delay(self, cmd):
        def impl(model):
            model.subtitle_delay = model.subtitle_delay - cmd.amount
            self._player.set_subtitle_delay(model.subtitle_delay)

        self._update(cmd.id, impl)

    # Private

    def _play_video_impl(self, cmd_id, video):
        def play_video(model):
            model.play(video)

        self._player.play(video.id, str(video.path))
        player = self._player_model()
        if player.subtitle_state is True:
            sub_stream = video.stream("subtitle", config["subtitle.language"])
            if sub_stream is not None:
                self._player.select_subtitle_stream(sub_stream.index)
        self._update(cmd_id, play_video)

    def _queue_video_impl(self, cmd_id, video):
        def queue_video(model):
            model.queue(video)

        self._update(cmd_id, queue_video)

    def _player_model(self):
        return self._player_repo.get_player()

    def _update(self, cmd_id, mutator, *args):
        def impl(ctx):
            model = self._player_model()
            mutator(model, *args)
            ctx.update(model)

        self._start_transaction(self._player_repo, cmd_id, impl)
