""" Playlist repository """

from OpenCast.domain.model.playlist import Playlist
from OpenCast.infra import Id

from .repository import Repository


class PlaylistRepo(Repository):
    def __init__(self, database, db_lock):
        super().__init__(database, db_lock, Playlist)

    def list_containing(self, video_id: Id):
        results = self._collection.search(lambda entity: str(video_id) in entity["ids"])
        return [self._entity.from_dict(result) for result in results]
