class DataFacade:
    def __init__(self, repo_factory):
        self._player_repo = repo_factory.make_player_repo()
        self._video_repo = repo_factory.make_video_repo()

    def player_repo(self):
        return self._player_repo

    def video_repo(self):
        return self._video_repo
