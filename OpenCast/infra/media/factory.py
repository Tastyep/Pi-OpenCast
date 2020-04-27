from pathlib import Path

from omxplayer.player import OMXPlayer

from .player_wrapper import PlayerWrapper


class MediaFactory:
    def __init__(self, evt_dispatcher):
        self._evt_dispatcher = evt_dispatcher

    def make_player(self):
        def player_factory(path, command, dbus_name, exit_callback):
            player = OMXPlayer(Path(path), command, dbus_name=dbus_name)
            player.exitEvent += exit_callback
            return player

        return PlayerWrapper(self._evt_dispatcher, player_factory)
