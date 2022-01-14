""" Entity identification operations """

from uuid import UUID, uuid3, uuid4


class IdentityService:
    # Randomly generated
    PLAYER_NS = UUID("d4ff6d03-f5de-4153-8382-7f7da42be559")
    VIDEO_NS = UUID("eee85b82-3d83-4531-80f8-c0b5e3b7cef3")
    PLAYLIST_NS = UUID("83c99116-66f0-4191-bc26-0e979ba2e835")
    ALBUM_NS = UUID("83c99116-66f0-4191-bc26-0e979ba2e836")
    ARTIST_NS = UUID("83c99116-66f0-4191-bc26-0e979ba2e837")

    @staticmethod
    def random():
        return uuid4()

    @staticmethod
    def id_workflow(workflow_cls, model_id):
        return uuid3(model_id, workflow_cls.__name__)

    @staticmethod
    def id_command(command_cls, model_id):
        return uuid3(model_id, command_cls.__name__)

    @classmethod
    def id_player(cls):
        return cls.PLAYER_NS

    @classmethod
    def id_video(cls, source):
        return uuid3(cls.VIDEO_NS, source)

    @classmethod
    def id_playlist(cls):
        return cls.random()

    @classmethod
    def id_album(cls, name):
        return uuid3(cls.ALBUM_NS, name)

    @classmethod
    def id_artist(cls, name):
        return uuid3(cls.ARTIST_NS, name)
