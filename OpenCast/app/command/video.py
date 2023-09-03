""" Video commands """

from dataclasses import field

from OpenCast.infra.media.downloader import Options as DownloadOptions

from .command import Command, Id, command


@command
class CreateVideo(Command):
    source: str
    collection_id: Id


@command
class DeleteVideo(Command):
    pass


@command
class RetrieveVideo(Command):
    output_directory: str
    dl_opts: DownloadOptions = field(default_factory=DownloadOptions)


@command
class ParseVideo(Command):
    pass


@command
class FetchVideoSubtitle(Command):
    language: str


@command
class SetVideoReady(Command):
    pass
