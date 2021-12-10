from test.util import TestCase

from OpenCast.infra.media.deezer import Deezer


class DeezerTest(TestCase):
    def setUp(self) -> None:
        self.deezer = Deezer()

    def test_search_w_artist_album(self):
        # https://stackoverflow.com/questions/46450545/testing-aiohttp-client-with-unittest-mock-patch
        # TODO: learn how to Mock the client session
        pass
