from dataclasses import dataclass
from uuid import UUID


def command(cls):
    return dataclass(cls, frozen=True)


@command
class Command:
    id: UUID
    model_id: UUID
