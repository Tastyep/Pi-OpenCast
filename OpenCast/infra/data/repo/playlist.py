""" Playlist repository """

from OpenCast.domain.model.playlist import Playlist

from .repository import Repository


class PlaylistRepo(Repository):
    def __init__(self, database):
        super().__init__(database, Playlist)
