from pathlib import Path


class SourceService:
    def __init__(self, video_downloader):
        self._downloader = video_downloader

    def is_playlist(self, source):
        return "/playlist" in source

    def unfold(self, source):
        return self._downloader.unfold_playlist(source)

    def fetch_metadata(self, video):
        if video.is_file():
            return {"title": str(Path(video.source).name)}
        return self._downloader.fetch_metadata(video.source, ["title"])
