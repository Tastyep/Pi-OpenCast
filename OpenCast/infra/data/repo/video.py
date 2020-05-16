from .memory import MemoryRepo


class VideoRepo(MemoryRepo):
    def __init__(self):
        super(VideoRepo, self).__init__()
