""" Video repository """

from OpenCast.domain.model.video import VideoSchema

from .repository import Repository


class VideoRepo(Repository):
    def __init__(self, database):
        super().__init__(database, VideoSchema())
