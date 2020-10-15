from test.shared.infra.data.producer import DataProducer
from test.util import TestCase

from OpenCast.config import config
from OpenCast.domain.service.identity import IdentityService
from OpenCast.domain.service.player import QueueingService
from OpenCast.infra.data.manager import DataManager, StorageType
from OpenCast.infra.data.repo.factory import RepoFactory


class QueueingServiceTest(TestCase):
    def setUp(self):
        repo_factory = RepoFactory()
        data_manager = DataManager(repo_factory)
        self.data_facade = data_manager.connect(StorageType.MEMORY)
        self.data_producer = DataProducer.make()
        self.video_repo = self.data_facade.video_repo
        self.playlist_repo = self.data_facade.playlist_repo

        self.service = QueueingService(
            self.data_facade.player_repo,
            self.data_facade.video_repo,
            self.data_facade.playlist_repo,
        )

        self.data_producer.player().populate(self.data_facade)
        self.queue_id = self.data_facade.player_repo.get_player().queue

    def test_queue_back(self):
        self.data_producer.player().video("source1").video("source2").video(
            "source3"
        ).parent_producer().video("source4").populate(self.data_facade)

        queue = self.playlist_repo.get(self.queue_id)
        videos = self.video_repo.list()
        queue.ids = self.service.queue(queue, videos[-1].id, front=False)
        expected = [video.id for video in videos]
        self.assertListEqual(expected, queue.ids)

    def test_queue_front_empty_queue(self):
        self.data_producer.video("source1").video("source2").video("source3").populate(
            self.data_facade
        )

        queue = self.playlist_repo.get(self.queue_id)
        videos = self.video_repo.list()
        for video in videos:
            queue.ids = self.service.queue(queue, video.id, front=True)
        expected = [video.id for video in reversed(videos)]
        self.assertListEqual(expected, queue.ids)

    def test_queue_front_playlist_empty_queue(self):
        self.data_producer.video("source1", collection_name="1").video(
            "source2", collection_name="1"
        ).video("source3", collection_name="1").populate(self.data_facade)

        queue = self.playlist_repo.get(self.queue_id)
        videos = self.video_repo.list()
        for video in videos:
            queue.ids = self.service.queue(queue, video.id, front=True)
        expected = [video.id for video in videos]
        self.assertListEqual(expected, queue.ids)

    def test_queue_front_playlist_while_playing(self):
        self.data_producer.player().video("source1", collection_name="1").video(
            "source2", collection_name="1"
        ).play("source1").parent_producer().video("source3", collection_name="2").video(
            "source4", collection_name="2"
        ).populate(
            self.data_facade
        )

        queue = self.playlist_repo.get(self.queue_id)
        videos = self.video_repo.list()
        playlist2 = [video for video in videos if video.collection_name == "2"]
        for video in playlist2:
            queue.ids = self.service.queue(queue, video.id, front=True)

        expected = [videos[0].id, videos[2].id, videos[3].id, videos[1].id]
        self.assertListEqual(expected, queue.ids)

    def test_queue_front_merge_playlist(self):
        self.data_producer.video("source1", collection_name="1").video("source2").video(
            "source3", collection_name="1"
        ).populate(self.data_facade)

        queue = self.playlist_repo.get(self.queue_id)
        videos = self.video_repo.list()
        queue.ids = self.service.queue(queue, videos[0].id, front=True)
        queue.ids = self.service.queue(queue, videos[1].id, front=False)
        queue.ids = self.service.queue(queue, videos[2].id, front=True)
        expected = [videos[0].id, videos[2].id, videos[1].id]
        self.assertListEqual(expected, queue.ids)

    def test_queue_no_merge_past_index(self):
        self.data_producer.player().video("source1", collection_name="1").video(
            "source2"
        ).play("source2").parent_producer().video(
            "source3", collection_name="1"
        ).populate(
            self.data_facade
        )

        queue = self.playlist_repo.get(self.queue_id)
        videos = self.video_repo.list()
        queue.ids = self.service.queue(queue, videos[2].id, front=True)
        expected = [videos[0].id, videos[1].id, videos[2].id]
        self.assertListEqual(expected, queue.ids)

    def test_next(self):
        self.data_producer.player().video("source1").video("source2").populate(
            self.data_facade
        )
        config.load_from_dict({"player": {"loop_last": False}})

        videos = self.video_repo.list()
        self.assertEqual(
            videos[1].id, self.service.next_video(self.queue_id, videos[0].id)
        )
        self.assertEqual(None, self.service.next_video(self.queue_id, videos[1].id))

    def test_next_loop_last(self):
        self.data_producer.player().video("source1").video("source2").populate(
            self.data_facade
        )
        config.load_from_dict({"player": {"loop_last": True}})

        videos = self.video_repo.list()
        self.assertEqual(
            videos[1].id, self.service.next_video(self.queue_id, videos[0].id)
        )
        self.assertEqual(
            videos[1].id, self.service.next_video(self.queue_id, videos[1].id)
        )

    def test_next_invalid_video(self):
        self.data_producer.player().video("source1").video("source2").populate(
            self.data_facade
        )
        config.load_from_dict({"player": {"loop_last": True}})

        video_id = IdentityService.id_video("source3")
        self.assertEqual(None, self.service.next_video(self.queue_id, video_id))
