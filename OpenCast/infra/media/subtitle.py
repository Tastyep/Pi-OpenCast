import logging
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


def load_from_video(video, language):
    video_name = video.path.name.rsplit(".", 1)[0]
    parent_path = video.path.parents[0]
    subtitle = "{}/{}.srt".format(parent_path, video_name)

    logger.debug(f"loading subtitles for {video}")
    srtFiles = list(parent_path.glob("*.srt"))
    if Path(subtitle) in srtFiles:
        logger.debug(f"found matching susbtitle file: {subtitle}")
        return subtitle

    logger.debug(f"searching softcoded subtitles from {video}")
    probe = dict()
    try:
        probe = ffmpeg.probe(str(video.path))
    except ffmpeg.Error as e:
        logger.error(f"ffprobe error: {e}")
        return None

    for stream in probe["streams"]:
        logger.debug(f"sub: {stream}")
        if (
            stream["codec_type"] == "subtitle"
            and stream["tags"]["language"] == language
        ):
            channel = "0:{}".format(stream["index"])
            logger.info(f"found matching sub: {subtitle}")
            try:
                ffmpeg.input(str(video.path)).output(subtitle, map=channel).global_args(
                    "-n"
                ).run()
                return subtitle
            except ffmpeg.Error as e:
                if e is None:  # The file probably exists
                    return subtitle
                logger.error(f"extraction error: {e.stderr}")

    logger.info(f"no subtitle found for: {video}")
    return None
