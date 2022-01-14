""" Playlist commands """

from dataclasses import field
from typing import List

from .command import Command, ModelId, command


@command
class CreatePlaylist(Command):
    name: str
    ids: List[ModelId] = field(default_factory=list)
    generated: bool = False


@command
class RenamePlaylist(Command):
    name: str


@command
class QueueVideo(Command):
    video_id: ModelId
    queue_front: bool


@command
class UpdatePlaylistContent(Command):
    ids: List[ModelId]


@command
class DeletePlaylist(Command):
    pass
