from OpenCast.domain.model.player import Player
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService


class DataProducer:
    def __init__(self):
        self._videos = []
        self._players = []

    def video(self, *args, **attrs):
        video_id = IdentityService.id_video(args[0])
        video = Video(video_id, *args)
        self._update_attrs(video, attrs)
        self._videos.append(video)
        return self

    def player(self, *args, **attrs):
        player_id = IdentityService.id_player()
        player = Player(player_id, *args)
        self._update_attrs(player, attrs)
        self._players.append(player)
        return self

    def populate(self, data_facade):
        self._populate(data_facade.video_repo, self._videos)
        self._populate(data_facade.player_repo, self._players)

    def _populate(self, repo, entities):
        for entity in entities:
            entity.release_events()
            repo.create(entity)
        entities.clear()

    def _update_attrs(self, model, attrs):
        for attr, value in attrs.items():
            setattr(model, attr, value)
