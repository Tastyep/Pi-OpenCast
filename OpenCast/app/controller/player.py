import structlog
from OpenCast.app.command import player as Cmd
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.event import player as player_events

from .controller import Controller


class PlayerController(Controller):
    def __init__(self, app_facade, data_facade):
        super(PlayerController, self).__init__(app_facade)

        self._logger = structlog.get_logger(__name__)
        self._player_repo = data_facade.player_repo
        self._video_repo = data_facade.video_repo

        self._observe(player_events)

    # Infra event handler interface implementation

    def _media_end_reached(self, evt):
        model = self._player_repo.get_player()
        video = model.next_video()
        if video is None:
            self._dispatch(Cmd.StopPlayer)
        else:
            self._dispatch(Cmd.PlayVideo, video.id)

    def _dispatch(self, cmd_cls, *args, **kwargs):
        player_id = IdentityService.id_player()
        return super(PlayerController, self)._dispatch(
            cmd_cls, player_id, *args, **kwargs
        )