""" Abstract representation of a command """


from dataclasses import dataclass

from OpenCast.domain.model import Id as ModelId
from OpenCast.infra import Id


def command(cls):
    return dataclass(cls, frozen=True)


@command
class Command:
    id: Id
    model_id: ModelId
