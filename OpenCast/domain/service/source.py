from pathlib import Path


class SourceService:
    def __init__(self, downloader):
        self._downloader = downloader

    def is_playlist(self, source):
        return "/playlist" in source

    def unfold(self, source):
        return self._downloader.unfold_playlist(source)

    def pick_stream_metadata(self, video):
        if video.from_disk():
            return {"title": str(Path(video.source).name)}
        return self._downloader.pick_stream_metadata(video.source, ["title"])
