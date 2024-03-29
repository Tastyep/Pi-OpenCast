""" The facade exposing persistence capabilities """
from threading import RLock


class DataFacade:
    def __init__(self, database, repo_factory):
        db_lock = RLock()
        self._player_repo = repo_factory.make_player_repo(database, db_lock)
        self._video_repo = repo_factory.make_video_repo(database, db_lock)
        self._playlist_repo = repo_factory.make_playlist_repo(database, db_lock)
        self._album_repo = repo_factory.make_album_repo(database, db_lock)
        self._artist_repo = repo_factory.make_artist_repo(database, db_lock)

    @property
    def player_repo(self):
        return self._player_repo

    @property
    def video_repo(self):
        return self._video_repo

    @property
    def playlist_repo(self):
        return self._playlist_repo

    @property
    def album_repo(self):
        return self._album_repo

    @property
    def artist_repo(self):
        return self._artist_repo
