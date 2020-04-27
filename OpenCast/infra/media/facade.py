class MediaFacade:
    def __init__(self, media_factory):
        self._player = media_factory.make_player()

    def player(self):
        return self._player
