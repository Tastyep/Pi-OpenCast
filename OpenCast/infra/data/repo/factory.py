""" Factory in charge of creating repository objects """


from .player import PlayerRepo
from .video import VideoRepo


class RepoFactory:
    def make_player_repo(self):
        return PlayerRepo()

    def make_video_repo(self):
        return VideoRepo()
