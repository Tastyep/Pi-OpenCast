from test.util import TestCase

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from OpenCast.domain.model.playlist import Playlist
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.repo.playlist import PlaylistRepo


class PlaylistRepositoryTest(TestCase):
    def setUp(self):
        database = TinyDB(storage=MemoryStorage)
        self.repo = PlaylistRepo(database)
        self.playlist_id = IdentityService.id_playlist()
        self.playlist = Playlist(self.playlist_id, "name")

    def test_list_containing(self):
        playlists = [
            Playlist(
                IdentityService.id_playlist(),
                "playlist_1",
                [
                    IdentityService.id_video("source1"),
                    IdentityService.id_video("source2"),
                ],
            ),
            Playlist(
                IdentityService.id_playlist(),
                "playlist_2",
                [
                    IdentityService.id_video("source3"),
                    IdentityService.id_video("source4"),
                ],
            ),
            Playlist(
                IdentityService.id_playlist(),
                "playlist_3",
                [
                    IdentityService.id_video("source1"),
                    IdentityService.id_video("source3"),
                ],
            ),
        ]
        for playlist in playlists:
            self.repo.create(playlist)

        result = self.repo.list_containing(IdentityService.id_video("source1"))
        self.assertEqual([playlists[0], playlists[2]], result)

        result = self.repo.list_containing(IdentityService.id_video("source4"))
        self.assertEqual([playlists[1]], result)

        result = self.repo.list_containing(IdentityService.id_video("source5"))
        self.assertEqual([], result)
