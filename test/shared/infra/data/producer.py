from OpenCast.domain.constant import HOME_PLAYLIST
from OpenCast.domain.model import Id
from OpenCast.domain.model.player import Player
from OpenCast.domain.model.playlist import Playlist
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService


class Population:
    def __init__(self):
        self._entities = {}
        self._last_entity = {}

    def add(self, cls, model_id, *args, **attrs):
        if "id" in attrs:
            model_id = attrs["id"]
            attrs.pop("id")

        id_to_entity = self._entities.get(cls, {})
        if model_id in id_to_entity:
            self._last_entity[cls] = model_id
            self._update_attrs(id_to_entity[model_id], attrs)
            return

        entity = cls(model_id, *args, **attrs)
        id_to_entity[entity.id] = entity
        self._last_entity[cls] = entity.id
        self._entities[cls] = id_to_entity

    def last(self, cls):
        entity_id = self._last_entity[cls]
        return self._entities[cls][entity_id]

    def find(self, cls, id: Id):
        collection = self._entities.get(cls, None)
        if collection is None:
            return None
        return collection.get(id, None)

    def select(self, cls, id: Id):
        self._last_entity[cls] = id

    def register(self, data_facade):
        def register(repo, entities):
            for entity in entities.values():
                entity.release_events()
                if repo.exists(entity.id):
                    repo.update(entity)
                else:
                    repo.create(entity)

        register(data_facade.player_repo, self._entities.get(Player, {}))
        register(data_facade.video_repo, self._entities.get(Video, {}))
        register(data_facade.playlist_repo, self._entities.get(Playlist, {}))

    def _update_attrs(self, entity, attrs):
        for attr, value in attrs.items():
            if getattr(entity, attr, None) is not None:
                setattr(entity, attr, value)
            else:
                setattr(entity._data, attr, value)


class DataProducer:
    def __init__(self, population):
        self._population = population

    @classmethod
    def make(cls):
        return cls(Population())

    def player(self, *args, **attrs):
        return PlayerProducer(self._population).player(*args, **attrs)

    def video(self, *args, **attrs):
        return VideoProducer(self._population).video(*args, **attrs)

    def playlist(self, *args, **attrs):
        return PlaylistProducer(self._population).playlist(*args, **attrs)

    def select(self, cls, id: Id):
        self._population.select(cls, id)
        if cls is Player:
            return PlayerProducer(self._population)
        if cls is Video:
            return VideoProducer(self._population)
        if cls is Playlist:
            return PlaylistProducer(self._population)
        return None

    def populate(self, data_facade):
        self._population.register(data_facade)


class PlayerProducer(DataProducer):
    def player(self, *args, **attrs):
        if self._population.find(Playlist, HOME_PLAYLIST.id) is None:
            PlaylistProducer(self._population).playlist(
                HOME_PLAYLIST.id, HOME_PLAYLIST.name, [], generated=True
            )
        player_id = IdentityService.id_player()
        self._population.add(Player, player_id, HOME_PLAYLIST.id, *args, **attrs)
        return self

    def video(self, *args, **attrs):
        VideoProducer(self._population).video(*args, **attrs)
        player = self._population.last(Player)
        queue = self._population.find(Playlist, player.queue)
        video = self._population.last(Video)
        queue.ids.append(video.id)
        return self

    def parent_producer(self):
        return super()

    def play(self, source: str, playlist_id=None):
        video_id = IdentityService.id_video(source)
        player = self._population.last(Player)
        if playlist_id is None:
            playlist_id = player.queue
        player.play(video_id, playlist_id)
        video = self._population.find(Video, video_id)
        video.start()
        return self

    def pause(self):
        self._population.last(Player).pause()
        return self


class VideoProducer(DataProducer):
    def video(self, *args, **attrs):
        video_id = IdentityService.id_video(args[0])
        self._population.add(Video, video_id, *args, **attrs)
        return self


class PlaylistProducer(DataProducer):
    def playlist(self, id: Id, *args, **attrs):
        self._population.add(Playlist, id, *args, **attrs)
        return self

    def video(self, *args, **attrs):
        VideoProducer(self._population).video(*args, **attrs)
        self._population.last(Playlist).ids.append(self._population.last(Video).id)
        return self
