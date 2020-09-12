""" Factory for creating workflow objects """

from .player import (
    QueuePlaylistWorkflow,
    QueueVideoWorkflow,
    StreamPlaylistWorkflow,
    StreamVideoWorkflow,
)
from .video import VideoWorkflow


class WorkflowFactory(object):
    """Creates instances of workflows."""

    def make_video_workflow(self, *args, **kwargs):
        return VideoWorkflow(*args, **kwargs)

    def make_queue_video_workflow(self, *args, **kwargs):
        return QueueVideoWorkflow(*args, **kwargs)

    def make_queue_playlist_video_workflow(self, *args, **kwargs):
        return QueuePlaylistWorkflow(*args, **kwargs)

    def make_stream_video_workflow(self, *args, **kwargs):
        return StreamVideoWorkflow(*args, **kwargs)

    def make_stream_playlist_video_workflow(self, *args, **kwargs):
        return StreamPlaylistWorkflow(*args, **kwargs)
