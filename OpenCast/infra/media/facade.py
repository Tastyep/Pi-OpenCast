class MediaFacade:
    def __init__(self, evt_dispatcher, media_factory):
        self._player = media_factory.make_player(evt_dispatcher)

    @property
    def player(self):
        return self._player
