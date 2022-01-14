""" Album repository """

from OpenCast.domain.model.album import Album
from OpenCast.infra import Id

from .repository import Repository


class AlbumRepo(Repository):
    def __init__(self, database, db_lock):
        super().__init__(database, db_lock, Album)

    def list_containing(self, video_id: Id):
        with self._lock:
            results = self._collection.search(
                lambda entity: str(video_id) in entity["ids"]
            )
        return [self._entity.from_dict(result) for result in results]
