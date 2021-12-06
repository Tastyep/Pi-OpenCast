""" Album commands """

from dataclasses import field
from typing import List, Optional

from .command import Command, ModelId, command


@command
class DeleteAlbum(Command):
    pass
