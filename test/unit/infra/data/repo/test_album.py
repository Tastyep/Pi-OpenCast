from test.util import TestCase
from threading import RLock

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

from OpenCast.domain.model.album import Album
from OpenCast.domain.service.identity import IdentityService
from OpenCast.infra.data.repo.album import AlbumRepo


class AlbumRepositoryTest(TestCase):
    def setUp(self):
        database = TinyDB(storage=MemoryStorage)
        self.repo = AlbumRepo(database, RLock())
        self.album_id = IdentityService.random()
        self.album = Album(self.album_id, "name")

    def test_list_containing(self):
        videos = [IdentityService.id_video(f"source{i}") for i in range(4)]

        albums = [
            Album(IdentityService.random(), "album_1", videos[:2]),
            Album(IdentityService.random(), "album_2", videos[2:]),
            Album(
                IdentityService.random(),
                "album_3",
                [videos[0], videos[2]],
            ),
        ]
        for album in albums:
            self.repo.create(album)

        result = self.repo.list_containing(videos[0])
        self.assertEqual([albums[0], albums[2]], result)

        result = self.repo.list_containing(videos[3])
        self.assertEqual([albums[1]], result)

        result = self.repo.list_containing(IdentityService.random())
        self.assertEqual([], result)
