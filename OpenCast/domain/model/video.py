from pathlib import Path


class Video:
    def __init__(self, source, playlist_id=None):
        self._source = source
        self._playlist_id = playlist_id
        self._path = None
        self._title = None
        self._subtitle = None

        path = Path(source)
        if path.is_file():
            self.path = source
            self._playlist_id = path.parent
            self._title = path.name

    def __repr__(self):
        title = "" if self._title is None else str(self._title)
        playlist_id = "" if self._playlist_id is None else str(self._playlist_id)
        return str(
            {"title": title, "source": str(self._source), "playlist_id": playlist_id}
        )

    def __eq__(self, other):
        return (
            other is not None
            and self._source == other._source
            and self._playlist_id == other._playlist_id
        )

    @property
    def source(self):
        return self._source

    @property
    def path(self):
        return self._path

    @property
    def title(self):
        return self._title

    @property
    def playlist_id(self):
        return self._playlist_id

    @property
    def subtitle(self):
        return self._subtitle

    def from_disk(self):
        return self._path is not None and str(self._path) == self._source

    @path.setter
    def path(self, path):
        self._path = Path(path)

    @title.setter
    def title(self, title):
        self._title = str(title.encode("ascii", "ignore"))

    @subtitle.setter
    def subtitle(self, subtitle):
        self._subtitle = subtitle
