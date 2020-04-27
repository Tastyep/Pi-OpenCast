from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from .command import Command


@dataclass
class AddVideo(Command):
    source: str
    playlist_id: UUID
    title: str
    path: Path


# @dataclass
# class IdentifyVideo(Command):
#     video_id: UUID


@dataclass
class DownloadVideo(Command):
    priority: bool


@dataclass
class FetchVideoSubtitle(Command):
    language: str
