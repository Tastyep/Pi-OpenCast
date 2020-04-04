import logging
from pathlib import Path

import ffmpeg

logger = logging.getLogger(__name__)


def load_from_video(video, language):
    video_name = video.path.name.rsplit(".", 1)[0]
    parent_path = video.path.parents[0]
    subtitle = "{}/{}.srt".format(parent_path, video_name)

    logger.debug("[subtitle] loading subtitles for {}".format(video))
    srtFiles = list(parent_path.glob("*.srt"))
    if Path(subtitle) in srtFiles:
        logger.debug("[subtitle] found matching susbtitle file: {}".format(subtitle))
        return subtitle

    logger.debug("[subtitle] searching softcoded subtitles from {}".format(video))
    probe = dict()
    try:
        probe = ffmpeg.probe(str(video.path))
    except ffmpeg.Error as e:
        logger.error("[subtitle] ffprobe error: {}".format(str(e)))
        return None

    for stream in probe["streams"]:
        logger.debug("sub: {}".format(stream))
        if (
            stream["codec_type"] == "subtitle"
            and stream["tags"]["language"] == language
        ):
            channel = "0:{}".format(stream["index"])
            logger.info("[subtitle] found matching sub: {}".format(subtitle))
            try:
                ffmpeg.input(str(video.path)).output(subtitle, map=channel).global_args(
                    "-n"
                ).run()
                return subtitle
            except ffmpeg.Error as e:
                if e is None:  # The file probably exists
                    return subtitle
                logger.error("[subtitle] extraction error: {}".format(e.stderr))

    logger.info("[subtitle] no subtitle found for: {}".format(video))
    return None
