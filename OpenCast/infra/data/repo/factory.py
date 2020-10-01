""" Factory in charge of creating repository objects """


from .player import PlayerRepo
from .video import VideoRepo


class RepoFactory:
    def make_player_repo(self, *args):
        return PlayerRepo(*args)

    def make_video_repo(self, *args):
        return VideoRepo(*args)
