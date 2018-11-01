import logging
import subtitle

from pathlib2 import Path

logger = logging.getLogger("App")


class Video(object):
    def __init__(self, url):
        self._url = url
        self._subtitles = []
        self._path = None
        self._title = None

        path = Path(url)
        if path.is_file():
            self.path = url

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
        self._title = title

    def __repr__(self):
        return str(self._url)

    def is_local(self):
        return self._path is not None

    def _load_subtitles(self):
        self._subtitles = subtitle.load_from_video_path(self._path)
