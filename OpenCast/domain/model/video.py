from dataclasses import dataclass
from pathlib import Path
from typing import List

from OpenCast.domain.event import video as Evt

from .entity import Entity, Id


@dataclass
class Stream:
    index: int
    type: str
    language: str


class Video(Entity):
    def __init__(self, id_: Id, source, playlist_id: Id):
        super().__init__(id_)
        self._source = source
        self._playlist_id = playlist_id
        self._title = None
        self._path = None
        self._streams = []
        self._subtitle = None

        self._record(Evt.VideoCreated, self._source, self._playlist_id)

    def __repr__(self):
        base_repr = super().__repr__()
        return f"{Video.__name__}({base_repr}, title='{self._title}', playlist={self._playlist_id})"

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
    def streams(self):
        return self._streams

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

    @streams.setter
    def streams(self, streams: List[Stream]):
        self._streams = streams
        self._record(Evt.VideoParsed, self._streams)

    @subtitle.setter
    def subtitle(self, subtitle: str):
        self._subtitle = subtitle
        self._record(Evt.VideoSubtitleFetched, self._subtitle)

    def from_disk(self):
        return Path(self._source).is_file()

    def stream(self, type: str, language: str):
        return next(
            (
                stream
                for stream in self._streams
                if stream.type == type and stream.language == language
            ),
            None,
        )

    def delete(self):
        self._record(Evt.VideoDeleted)
