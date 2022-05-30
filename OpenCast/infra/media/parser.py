""" Parser of disk available medias """

from threading import Condition

import structlog
from vlc import EventType, MediaParsedStatus, MediaParseFlag, TrackType

from .error import VideoParsingError


class VideoParser:
    def __init__(self, vlc_instance):
        self._logger = structlog.get_logger(__name__)
        self._vlc = vlc_instance

    def parse_streams(self, video_path: str):
        media = self._vlc.media_new_path(video_path)
        cv = Condition()

        def parse_status_update(_):
            with cv:
                cv.notify()

        def raise_on_error():
            status = media.get_parsed_status()
            if status != MediaParsedStatus.done:
                self._logger.error(
                    "Stream parsing error", video=video_path, status=status
                )
                raise VideoParsingError(
                    f"Can't parse streams from '{video_path}', status='{str(status)}'"
                )

        media.event_manager().event_attach(
            EventType.MediaParsedChanged, parse_status_update
        )
        with cv:
            if media.parse_with_options(MediaParseFlag.local, timeout=5000) == -1:
                raise_on_error()
            cv.wait_for(media.is_parsed)

        raise_on_error()
        streams = media.tracks_get()
        media.release()
        if streams is None:
            self._logger.error("No stream found", video=video_path)
            raise VideoParsingError(f"No stream found for '{video_path}'")

        type_to_code = {
            TrackType.audio: "audio",
            TrackType.video: "video",
            TrackType.ext: "subtitle",
        }
        return [
            (
                stream.id,
                type_to_code.get(stream.type, "unknown"),
                None
                # None if stream.language is None else stream.language.decode("UTF-8"),
                # For some reason the language attribute might not be available
            )
            for stream in streams
        ]
