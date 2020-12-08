""" Video repository """

from OpenCast.domain.model.video import Video

from .repository import Repository


class VideoRepo(Repository):
    def __init__(self, database, db_lock):
        super().__init__(database, db_lock, Video)
