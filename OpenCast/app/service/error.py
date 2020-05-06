from dataclasses import dataclass
from uuid import UUID

from OpenCast.app.command.command import Command


@dataclass
class OperationError:
    def __init__(self, cmd: Command, error: str):
        self.id = cmd.id
        self.cmd = cmd
        self.error = error

    id: UUID
    cmd: Command
    error: str
