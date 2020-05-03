from pathlib import Path

from OpenCast.domain.event import video as Evt

from .entity import Entity


class Video(Entity):
    def __init__(self, id_, source, playlist_id):
        super(Video, self).__init__(id_)
        self._source = source
        self._playlist_id = playlist_id
        self._title = None
        self._path = None
        self._subtitle = None

        self._record(Evt.VideoCreated, self._source, self._playlist_id)

    def __repr__(self):
        return f"{Video.__name__}(title='{self._title}', playlist={self._playlist_id})"

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

    @title.setter
    def title(self, title):
        self._title = str(title.encode("ascii", "ignore"))

    @title.setter
    def title(self, title: str):
        self._title = title
        self._record(Evt.VideoIdentified, self._title)

    @path.setter
    def path(self, path: Path):
        self._path = path
        self._record(Evt.VideoRetrieved, self._path)

    @subtitle.setter
    def subtitle(self, subtitle):
        self._subtitle = subtitle
        self._record(Evt.VideoSubtitleFetched, self._subtitle)

    def is_file(self):
        return Path(self._source).is_file()
