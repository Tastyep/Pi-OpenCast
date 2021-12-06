from unittest.mock import Mock


class DataFacadeMock(Mock):
    def __init__(self):
        super(DataFacadeMock, self).__init__()
        self.player_repo = Mock()
        self.video_repo = Mock()
        self.playlist_repo = Mock()
        self.album_repo = Mock()
