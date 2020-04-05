import uuid

from OpenCast.domain.model.video import Video


class PlaylistService:
    def __init__(self, video_downloader):
        self._downloader = video_downloader

    def is_playlist(self, url):
        return "/playlist" in url

    def unfold(self, playlist_url):
        # Generate a unique ID for the playlist
        playlist_id = uuid.uuid4()
        urls = self._downloader.unfold_playlist(playlist_url)
        return [Video(u, playlist_id) for u in urls]
