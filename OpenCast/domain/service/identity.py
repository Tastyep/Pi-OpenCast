from uuid import uuid3, uuid4


class IdentityService:
    PLAYER_NS = uuid4()
    VIDEO_NS = uuid4()
    PLAYLIST_NS = uuid4()

    @staticmethod
    def id_workflow(workflow_cls, model_id):
        return uuid3(model_id, workflow_cls.__name__)

    @staticmethod
    def id_command(command_cls, model_id):
        return uuid3(model_id, command_cls.__name__)

    @classmethod
    def id_player(cls):
        return uuid3(cls.PLAYER_NS, str(cls.PLAYER_NS))

    @classmethod
    def id_video(cls, source):
        return uuid3(cls.VIDEO_NS, source)

    @classmethod
    def id_playlist(cls, source):
        return uuid3(cls.PLAYLIST_NS, source)
