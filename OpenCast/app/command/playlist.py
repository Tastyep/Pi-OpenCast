""" Playlist commands """

from dataclasses import field
from typing import List, Optional

from .command import Command, ModelId, command


@command
class CreatePlaylist(Command):
    name: str
    ids: List[ModelId] = field(default_factory=list)


@command
class RenamePlaylist(Command):
    name: str


@command
class QueueVideo(Command):
    video_id: ModelId
    queue_front: bool
    prev_video_id: Optional[ModelId]


@command
class UpdatePlaylistContent(Command):
    ids: List[ModelId]


@command
class DeletePlaylist(Command):
    pass
