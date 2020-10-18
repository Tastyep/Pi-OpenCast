""" Factory for creating IO objects """

from .channel import JanusChannel, PollingChannel


class IoFactory:
    def make_polling_channel(self, *args):
        return PollingChannel(*args)

    def make_janus_channel(self, *args):
        return JanusChannel(*args)
