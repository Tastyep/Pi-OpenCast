""" Definitions of domain constants """

from dataclasses import dataclass

from OpenCast.domain.model import Id
from OpenCast.domain.service.identity import IdentityService


@dataclass
class HomePlaylist:
    id: Id
    name: str


HOME_PLAYLIST = HomePlaylist(IdentityService.PLAYLIST_NS, "Home")
