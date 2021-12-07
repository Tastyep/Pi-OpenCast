from test.util import TestCase
from threading import RLock

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from OpenCast.domain.model.artist import Artist
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.repo.artist import ArtistRepo


class ArtistRepositoryTest(TestCase):
    def setUp(self):
        database = TinyDB(storage=MemoryStorage)
        self.repo = ArtistRepo(database, RLock())
        self.artist_id = IdentityService.random()
        self.artist = Artist(self.artist_id, "name")

    def test_list_containing(self):
        videos = [IdentityService.id_video(f"source{i}") for i in range(4)]

        artists = [
            Artist(IdentityService.random(), "artist_1", videos[:2]),
            Artist(IdentityService.random(), "artist_2", videos[2:]),
            Artist(
                IdentityService.random(),
                "artist_3",
                [videos[0], videos[2]],
            ),
        ]
        for artist in artists:
            self.repo.create(artist)

        result = self.repo.list_containing(videos[0])
        self.assertEqual([artists[0], artists[2]], result)

        result = self.repo.list_containing(videos[3])
        self.assertEqual([artists[1]], result)

        result = self.repo.list_containing(IdentityService.random())
        self.assertEqual([], result)
