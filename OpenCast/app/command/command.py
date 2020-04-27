from dataclasses import dataclass
from uuid import UUID


@dataclass
class Command:
    id: UUID
    model_id: UUID
