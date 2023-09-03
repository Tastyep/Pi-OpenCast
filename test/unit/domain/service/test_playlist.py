from test.util import TestCase

from OpenCast.domain.service.identity import IdentityService
from OpenCast.domain.service.playlist import shrink_playlist


class PlaylistServiceTest(TestCase):
    def test_shrink_smaller(self):
        ids = [IdentityService.id_video(f"{i}") for i in range(10)]
        expected = shrink_playlist(ids, len(ids) + 1, [])

        self.assertListEqual(expected, ids)

    def test_shrink_equal(self):
        ids = [IdentityService.id_video(f"{i}") for i in range(10)]
        expected = shrink_playlist(ids, len(ids) + 1, [])

        self.assertListEqual(expected, ids)

    def test_shrink_larger(self):
        ids = [IdentityService.id_video(f"{i}") for i in range(10)]
        expected = shrink_playlist(ids, len(ids) - 1, [])

        self.assertListEqual(expected, ids[1:])
    
    def test_shrink_larger_blacklist_first(self):
        ids = [IdentityService.id_video(f"{i}") for i in range(10)]
        blacklist = [ids[0]]
        expected = shrink_playlist(ids, len(ids) - 1, blacklist)

        self.assertListEqual(expected, blacklist + ids[2:])
    
    def test_shrink_larger_blacklist_non_continuous(self):
        ids = [IdentityService.id_video(f"{i}") for i in range(10)]
        blacklist = [ids[0], ids[2], ids[5]]
        expected = shrink_playlist(ids, len(ids) - 4, blacklist)

        self.assertListEqual(expected, blacklist + ids[7:])
