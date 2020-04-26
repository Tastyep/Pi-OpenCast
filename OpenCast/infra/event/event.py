from dataclasses import dataclass
from uuid import UUID


@dataclass
class Event:
    id: UUID
