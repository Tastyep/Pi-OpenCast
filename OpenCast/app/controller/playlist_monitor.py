""" Playlist capabilities monitoring routes """

import structlog

from OpenCast.app.command import playlist as Cmd
from OpenCast.app.service.error import OperationError
from OpenCast.domain.event import playlist as PlaylistEvt
from OpenCast.domain.model import Id
from OpenCast.domain.model.playlist import PlaylistSchema
from OpenCast.domain.service.identity import IdentityService

from .monitor import MonitorController


class PlaylistMonitController(MonitorController):
    def __init__(self, app_facade, infra_facade, data_facade):
        logger = structlog.get_logger(__name__)
        super().__init__(logger, app_facade, infra_facade, "/playlists")
        self._playlist_repo = data_facade.playlist_repo
        self._video_repo = data_facade.video_repo

        self._route("GET", "/", handle=self.list)
        self._route("GET", "/{id:" + self.UUID + "}", handle=self.get)
        self._route("POST", "/", handle=self.create)
        self._route("PATCH", "/{id:" + self.UUID + "}", handle=self.update)
        self._route("DELETE", "/{id:" + self.UUID + "}", handle=self.delete)
        self._route("GET", "/{id:" + self.UUID + "}/videos", handle=self.list_videos)

    async def list(self, req):
        playlists = self._playlist_repo.list()
        return self._ok(playlists)

    async def get(self, req):
        id = Id(req.match_info["id"])
        playlist = self._playlist_repo.get(id)
        if playlist is None:
            return self._not_found()
        return self._ok(playlist)

    async def create(self, req):
        data = await req.json()
        errors = PlaylistSchema().validate(data)
        if errors:
            return self._bad_request("Schema validation error.", errors)

        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            playlist = self._playlist_repo.get(evt.model_id)
            channel.send(self._ok(playlist))

        def on_error(evt):
            channel.send(self._bad_request(evt.error))

        self._observe_dispatch(
            {PlaylistEvt.PlaylistCreated: on_success, OperationError: on_error},
            Cmd.CreatePlaylist,
            IdentityService.id_playlist(),
            **data,
        )

        return await channel.receive()

    async def update(self, req):
        id = Id(req.match_info["id"])
        if not self._playlist_repo.exists(id):
            return self._not_found()

        data = await req.json()
        errors = PlaylistSchema().validate(data)
        if errors:
            return self._bad_request("Schema validation error.", errors)

        field_count = len(data)
        success_count = 0
        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            nonlocal success_count
            success_count += 1
            if success_count == field_count:
                playlist = self._playlist_repo.get(evt.model_id)
                channel.send(self._ok(playlist))

        def on_error(evt):
            channel.send(self._bad_request(evt.error))

        def update_field(field, cmd_cls, evt_cls):
            self._observe_dispatch(
                {
                    evt_cls: on_success,
                    OperationError: on_error,
                },
                cmd_cls,
                id,
                data[field],
            )

        for field in data:
            if field == "name":
                update_field(field, Cmd.RenamePlaylist, PlaylistEvt.PlaylistRenamed)
            elif field == "ids":
                update_field(
                    field, Cmd.UpdatePlaylistContent, PlaylistEvt.PlaylistContentUpdated
                )

        return await channel.receive()

    async def delete(self, req):
        id = Id(req.match_info["id"])
        if not self._playlist_repo.exists(id):
            return self._not_found()

        channel = self._io_factory.make_janus_channel()

        def on_success(evt):
            channel.send(self._no_content())

        self._observe_dispatch(
            {PlaylistEvt.PlaylistDeleted: on_success}, Cmd.DeletePlaylist, id
        )

        return await channel.receive()

    async def list_videos(self, req):
        id = Id(req.match_info["id"])
        playlist = self._playlist_repo.get(id)
        if playlist is None:
            return self._not_found()

        videos = self._video_repo.list(playlist.ids)
        return self._ok(videos)
