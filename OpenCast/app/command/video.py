from uuid import UUID

from .command import Command, command


@command
class CreateVideo(Command):
    source: str
    playlist_id: UUID


@command
class DeleteVideo(Command):
    pass


@command
class IdentifyVideo(Command):
    pass


@command
class RetrieveVideo(Command):
    output_directory: str


@command
class FetchVideoSubtitle(Command):
    language: str
