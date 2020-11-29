""" Factory for creating IO objects """

from .channel import JanusChannel


class IoFactory:
    def make_janus_channel(self, *args):
        return JanusChannel(*args)
