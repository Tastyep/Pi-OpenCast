from dataclasses import dataclass

from OpenCast.infra import Id


@dataclass
class OperationError:
    id: Id
    error: str
