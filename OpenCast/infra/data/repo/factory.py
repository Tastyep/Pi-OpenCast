from .player_repo import PlayerRepo
from .video_repo import VideoRepo


class RepoFactory(object):
    def make_player_repo(self):
        return PlayerRepo()

    def make_video_repo(self):
        return VideoRepo()
