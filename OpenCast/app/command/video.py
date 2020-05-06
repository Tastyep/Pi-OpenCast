from dataclasses import dataclass
from uuid import UUID

from .command import Command


@dataclass
class CreateVideo(Command):
    source: str
    playlist_id: UUID


@dataclass
class DeleteVideo(Command):
    pass


@dataclass
class IdentifyVideo(Command):
    pass


@dataclass
class RetrieveVideo(Command):
    priority: bool


@dataclass
class FetchVideoSubtitle(Command):
    language: str
