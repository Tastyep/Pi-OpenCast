""" Video commands """

from .command import Command, command


@command
class CreateVideo(Command):
    source: str


@command
class DeleteVideo(Command):
    pass


@command
class RetrieveVideo(Command):
    output_directory: str


@command
class ParseVideo(Command):
    pass


@command
class FetchVideoSubtitle(Command):
    language: str
