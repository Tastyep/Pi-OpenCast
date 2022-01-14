""" Set of exceptions related to operation errors """

from dataclasses import dataclass, field

from OpenCast.infra import Id


@dataclass
class OperationError:
    id: Id
    error: str
    details: dict = field(default_factory=dict)
