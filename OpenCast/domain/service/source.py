from pathlib import Path


class SourceService:
    def __init__(self, video_downloader):
        self._downloader = video_downloader

    def is_playlist(self, source):
        return "/playlist" in source

    def unfold(self, source):
        return self._downloader.unfold_playlist(source)

    def fetch_metadata(self, source):
        path = Path(source)
        if path.is_file():
            return {"online": False, "title": path.parent}

        data = {"online": True}
        metadata = self._downloader.fetch_metadata(source, ["title"])
        if metadata is None:
            data["error"] = "Not available"
            return data
        return {**data, **metadata}
