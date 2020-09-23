""" Infrastructural components exposed the applicative layer """

from .io.server import make_server


class InfraFacade:
    def __init__(self, io_factory, media_factory, service_factory):
        self._io_factory = io_factory
        self._media_factory = media_factory
        self._service_factory = service_factory

        self._server = make_server()

    # IO objects

    @property
    def io_factory(self):
        return self._io_factory

    @property
    def service_factory(self):
        return self._service_factory

    @property
    def server(self):
        return self._server

    # Media objects

    @property
    def media_factory(self):
        return self._media_factory
