from .memory_repository import MemoryRepository


class VideoRepo(MemoryRepository):
    def __init__(self):
        super(VideoRepo, self).__init__()
