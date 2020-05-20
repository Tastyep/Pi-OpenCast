from pathlib import Path

from omxplayer.player import OMXPlayer

from .player_wrapper import PlayerWrapper


class MediaFactory:
    def make_player(self, *args):
        def player_factory(path, command, dbus_name, exit_callback):
            player = OMXPlayer(Path(path), command, dbus_name=dbus_name)
            player.exitEvent += exit_callback
            return player

        return PlayerWrapper(player_factory, *args)
