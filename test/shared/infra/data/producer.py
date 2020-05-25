from OpenCast.domain.model.player import Player
from OpenCast.domain.model.video import Video
from OpenCast.domain.service.identity import IdentityService


class Population:
    def __init__(self):
        self._entities = {}
        self._last_entity = {}

    def add(self, cls, id, args, attrs):
        id_to_entity = self._entities.get(cls, {})
        if id in id_to_entity:
            self._last_entity[cls] = id
            self._update_attrs(id_to_entity[id], attrs)
            return

        entity = cls(id, *args)
        self._update_attrs(entity, attrs)
        id_to_entity[id] = entity
        self._last_entity[cls] = id
        self._entities[cls] = id_to_entity

    def last(self, cls):
        entity_id = self._last_entity[cls]
        return self._entities[cls][entity_id]

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

    def _update_attrs(self, entity, attrs):
        for attr, value in attrs.items():
            setattr(entity, attr, value)


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

    def populate(self, data_facade):
        self._population.register(data_facade)


class PlayerProducer(DataProducer):
    def __init__(self, population):
        super(PlayerProducer, self).__init__(population)

    def player(self, *args, **attrs):
        player_id = IdentityService.id_player()
        self._population.add(Player, player_id, args, attrs)
        return self

    def video(self, *args, **attrs):
        VideoProducer(self._population).video(*args, **attrs)
        self._population.last(Player).queue(self._population.last(Video))
        return self

    def play(self):
        self._population.last(Player).play(self._population.last(Video))
        return self

    def pause(self):
        self._population.last(Player).pause()
        return self


class VideoProducer(DataProducer):
    def __init__(self, population):
        super(VideoProducer, self).__init__(population)

    def video(self, *args, **attrs):
        video_id = IdentityService.id_video(args[0])
        self._population.add(Video, video_id, args, attrs)
        return self
