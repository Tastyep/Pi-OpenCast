from .playlist_service import PlaylistService


class ServiceFactory:
    def make_playlist_service(self, downloader):
        return PlaylistService(downloader)
