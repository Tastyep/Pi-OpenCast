from unittest.mock import Mock

from OpenCast.infra.event.player import PlayerStopped


def make_player_mock(evt_dispatcher):
    def dispatch_stopped(op_id):
        evt_dispatcher.dispatch(PlayerStopped(op_id))

    player = Mock()
    player.stop = Mock(side_effect=dispatch_stopped)
    return player
