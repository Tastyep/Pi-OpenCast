from dataclasses import dataclass

from OpenCast.infra.event.event import Event


@dataclass
class MediaEndReached(Event):
    pass
