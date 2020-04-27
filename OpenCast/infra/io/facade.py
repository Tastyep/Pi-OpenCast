class IoFacade:
    def __init__(self, io_factory):
        self._ffmpeg_wrapper = io_factory.make_ffmpeg_wrapper()
        self._server = io_factory.make_server()
        self._video_downloader = io_factory.make_video_downloader()

    def ffmpeg_wrapper(self):
        return self._ffmpeg_wrapper

    def server(self):
        return self._server

    def video_downloader(self):
        return self._video_downloader
