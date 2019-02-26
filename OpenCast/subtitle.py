import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_from_video_path(video_path):
    path = Path(video_path)
    video_name = path.name.rsplit('.', 1)[0]
    video_path = path.parents[0]

    srtFiles = list(video_path.glob('*.srt'))
    matchingSubs = [str(srt) for srt in srtFiles if video_name in str(srt)]

    return matchingSubs

    # NOTE: Add future support for a subtitle_path config entry.
    # subtitle_path = ['./subtitle/', '/Video/subtitles']
