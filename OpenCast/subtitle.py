import logging
from pathlib import Path

import ffmpeg

from .config import config

logger = logging.getLogger(__name__)
config = config['Subtitle']


def load_from_video_path(path):
    video_name = path.name.rsplit('.', 1)[0]
    parent_path = path.parents[0]
    subtitle = '{}/{}.srt'.format(parent_path, video_name)

    logger.debug("[subtitle] loading subtitles for {}".format(path))
    srtFiles = list(parent_path.glob('*.srt'))
    if Path(subtitle) in srtFiles:
        logger.debug(
            "[subtitle] found matching susbtitle file: {}".format(subtitle)
        )
        return subtitle

    logger.debug(
        "[subtitle] searching softcoded subtitles from {}".format(path)
    )
    probe = ffmpeg.probe(str(path))
    for stream in probe['streams']:
        logger.debug("sub: {}".format(stream))
        if stream['codec_type'] == 'subtitle' and stream['tags'][
            'language'] == config.language:
            channel = '0:{}'.format(stream['index'])
            logger.info("[subtitle] found matching sub: {}".format(subtitle))
            try:
                ffmpeg.input(str(path)).output(
                    subtitle, map=channel
                ).global_args('-n').run()
                return subtitle
            except ffmpeg.Error as e:
                if e is None:  # The file probably exists
                    return subtitle
                logger.error("[subtitle] extraction error: {}".format(e.stderr))

    return None
