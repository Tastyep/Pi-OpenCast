""" Events emitted by the media downloader """

from dataclasses import dataclass

from OpenCast.infra import Id
from OpenCast.infra.event.event import Event


@dataclass
class DownloadSuccess(Event):
    pass


@dataclass
class DownloadError(Event):
    error: str


@dataclass
class DownloadInfo(Event):
    model_id: Id
    total_bytes: int
    downloaded_bytes: int
