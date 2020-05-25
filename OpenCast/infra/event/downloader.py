from dataclasses import dataclass

from OpenCast.infra.event.event import Event


@dataclass
class DownloadSuccess(Event):
    pass


@dataclass
class DownloadError(Event):
    error: str
