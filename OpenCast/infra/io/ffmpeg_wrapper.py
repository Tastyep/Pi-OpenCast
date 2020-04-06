import logging

import ffmpeg


class FFmpegWrapper:
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def probe(self, file_path):
        try:
            return ffmpeg.probe(str(file_path))
        except ffmpeg.Error as e:
            self._logger.error(f"ffprobe error: {e}")
            return None

    def extract_stream(self, src, dest, stream_idx, override):
        channel = "0:{}".format(stream_idx)
        args = []
        if override is True:
            args.append("-n")
        try:
            ffmpeg.input(str(src)).output(str(dest), map=channel).global_args(
                *args
            ).run()
            return dest
        except ffmpeg.Error as e:
            if e is None and override is True:  # The file probably exists
                return dest
            self._logger.error(f"stream extraction error: {e.stderr}")
            return None
