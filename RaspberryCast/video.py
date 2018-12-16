import logging

from pathlib import Path
from . import subtitle

logger = logging.getLogger(__name__)


class Video(object):
    def __init__(self, url, playlistId=None):
        self._url = url
        self._playlistId = playlistId
        self._path = None
        self._title = None
        self._subtitles = []

        path = Path(url)
        if path.is_file():
            self.path = url
            self._playlistId = self._path.parent
            self._title = self._path.name

    @property
    def url(self):
        return self._url

    @property
    def subtitles(self):
        return self._subtitles

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = Path(path)
        self._load_subtitles()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = str(title.encode('ascii', 'ignore'))

    @property
    def playlistId(self):
        return self._playlistId

    def __repr__(self):
        title = '' if self._title is None else str(self._title)
        return str({'title': title, 'url': str(self._url)})

    def __eq__(self, other):
        return (self._url is other._url and
                self._playlistId is other._playlistId)

    def is_local(self):
        return self._path is not None

    def _load_subtitles(self):
        self._subtitles = subtitle.load_from_video_path(self._path)
