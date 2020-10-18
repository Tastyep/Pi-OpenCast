""" Factory in charge of creating repository objects """


from .player import PlayerRepo
from .playlist import PlaylistRepo
from .video import VideoRepo


class RepoFactory:
    def make_player_repo(self, *args):
        return PlayerRepo(*args)

    def make_video_repo(self, *args):
        return VideoRepo(*args)

    def make_playlist_repo(self, *args):
        return PlaylistRepo(*args)
