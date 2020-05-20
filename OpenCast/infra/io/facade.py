class IoFacade:
    def __init__(self, evt_dispatcher, io_factory, downloader_executor):
        self._ffmpeg_wrapper = io_factory.make_ffmpeg_wrapper()
        self._server = io_factory.make_server()
        self._video_downloader = io_factory.make_video_downloader(
            evt_dispatcher, downloader_executor
        )

    @property
    def ffmpeg_wrapper(self):
        return self._ffmpeg_wrapper

    @property
    def server(self):
        return self._server

    @property
    def video_downloader(self):
        return self._video_downloader
