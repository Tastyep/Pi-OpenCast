from dataclasses import dataclass
from uuid import UUID


@dataclass
class OperationError:
    id: UUID
    error: str
