import logging
from pathlib import Path

from . import subtitle

logger = logging.getLogger(__name__)


class Video(object):
    def __init__(self, url, playlist_id=None):
        self._url = url
        self._playlist_id = playlist_id
        self._path = None
        self._title = None
        self._subtitle = None

        path = Path(url)
        if path.is_file():
            self.path = url
            self._playlist_id = path.parent
            self._title = path.name

    def __repr__(self):
        title = '' if self._title is None else str(self._title)
        playlist_id = '' if self._playlist_id is None else str(
            self._playlist_id
        )
        return str({
            'title': title,
            'url': str(self._url),
            'playlist_id': playlist_id
        })

    def __eq__(self, other):
        return (
            self._url == other._url and self._playlist_id == other._playlist_id
        )

    @property
    def url(self):
        return self._url

    @property
    def subtitle(self):
        return self._subtitle

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        self._path = Path(path)
        if self.is_local():
            self._load_subtitle()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, title):
        self._title = str(title.encode('ascii', 'ignore'))

    @property
    def playlist_id(self):
        return self._playlist_id

    def is_local(self):
        return self._path is not None and str(self._path) == self._url

    def _load_subtitle(self):
        self._subtitle = subtitle.load_from_video_path(self._path)
