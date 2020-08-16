from OpenCast.app.command import video as Cmd
from OpenCast.domain.event import video as Evt
from OpenCast.domain.model import Id

from .monitor import MonitorController


class VideoMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        super().__init__(app_facade, infra_facade, "/video")
        self._video_repo = data_facade.video_repo

        self._route("GET", "/", handle=self._list)
        self._route("GET", "/{id}", handle=self._get)
        self._route("DELETE", "/{id}", handle=self._delete)

    async def _list(self, req):
        videos = self._video_repo.list()
        return self._ok(videos)

    async def _get(self, req):
        id = Id(req.match_info["id"])
        video = self._video_repo.get(id)
        if video is None:
            return self._not_found()
        return self._ok(video)

    async def _delete(self, req):
        id = Id(req.match_info["id"])
        if not self._video_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            channel.send(self._no_content())

        self._observe_dispatch({Evt.VideoDeleted: on_success}, Cmd.DeleteVideo, id)

        return await channel.receive()
