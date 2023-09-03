from typing import List

from OpenCast.domain.model import Id


# NOTE: Add an option to skip albums related to blacklisted tracks
def shrink_playlist(playlist_ids: List[Id], max_size: int, blacklist: List[Id]):
    if len(playlist_ids) <= max_size:
        return playlist_ids

    result = []
    oversize = len(playlist_ids) - max_size
    idx = 0
    for id in playlist_ids:
        idx += 1
        if id in blacklist:
            result.append(id)
        else:
            oversize -= 1
            if oversize == 0:
                break

    return result + playlist_ids[idx:]
