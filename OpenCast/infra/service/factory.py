from .subtitle import SubtitleConverter


class ServiceFactory:
    def make_subtitle_converter(self, *args):
        return SubtitleConverter(*args)
