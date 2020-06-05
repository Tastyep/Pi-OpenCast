from .server import Server


class IoFactory:
    def make_server(self, *args):
        return Server(*args)
