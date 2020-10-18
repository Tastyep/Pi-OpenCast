""" The facade exposing persistence capabilities """


class DataFacade:
    def __init__(self, database, repo_factory):
        self._player_repo = repo_factory.make_player_repo(database)
        self._video_repo = repo_factory.make_video_repo(database)
        self._playlist_repo = repo_factory.make_playlist_repo(database)

    @property
    def player_repo(self):
        return self._player_repo

    @property
    def video_repo(self):
        return self._video_repo

    @property
    def playlist_repo(self):
        return self._playlist_repo
