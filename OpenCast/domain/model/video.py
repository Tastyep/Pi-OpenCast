from pathlib import Path

from OpenCast.domain.event import video as Evt

from .entity import Entity


class Video(Entity):
    def __init__(self, id_, source, playlist_id, title, path):
        super(Video, self).__init__(id_)
        self._source = source
        self._playlist_id = playlist_id
        self._title = title
        self._path = Path(path)
        self._subtitle = None

        self._record(
            Evt.VideoCreated, self._source, self._playlist_id, self._title, self._path
        )

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

    @subtitle.setter
    def subtitle(self, subtitle):
        self._subtitle = subtitle
        self._record(Evt.VideoSubtitleFetched, self._subtitle)

    def downloaded(self):
        self._record(Evt.VideoDownloaded)

    def is_file(self):
        return self._path.is_file()
