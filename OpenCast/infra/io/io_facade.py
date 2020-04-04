class IoFacade(object):
    def __init__(self, io_factory):
        self._server = io_factory.make_server()
        self._video_downloader = io_factory.make_video_downloader()

    def server(self):
        return self._server

    def video_downloader(self):
        return self._video_downloader
