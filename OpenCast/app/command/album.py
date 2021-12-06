""" Album commands """

from dataclasses import field
from typing import List, Optional

from .command import Command, ModelId, command


@command
class CreateAlbum(Command):
    name: str
    ids: List[ModelId] = field(default_factory=list)
    thumbnail: Optional[str] = None


@command
class UpdateAlbumVideos(Command):
    ids: List[ModelId]


@command
class DeleteAlbum(Command):
    pass
