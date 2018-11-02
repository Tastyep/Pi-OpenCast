import logging
import youtube_dl
import media_player
import video_downloader
import uuid

from video import Video

logger = logging.getLogger("App")
player = media_player.make_player(0)
downloader = video_downloader.make_video_downloader()


def play_video(video):
    player.queue(video, first=True)
    player.play()


def stream_video(url):
    logger.debug('stream video, URL="' + url + '"')
    player.stop()

    video = Video(url)
    if video.is_local():
        player.play(video)
        return

    if '/playlist' in url:
        # Generate a unique ID for the playlist
        playlistId = uuid.uuid4()
        urls = parse_playlist(url)
        videos = [Video(u, playlistId) for u in urls]
        downloader.queue(videos,
                         play_video,
                         first=True)
        return

    downloader.queue([video],
                     play_video,
                     first=True)


def queue_video(url):
    logger.debug('queue video, URL="' + url + '"')

    if '/playlist' in url:
        urls = parse_playlist(url)
        videos = [Video(u) for u in urls]
        logger.debug("Playlist url unwound to %r" % (videos))
        downloader.queue(urls, lambda video: player.queue(video))
    else:
        downloader.queue([url], lambda video: player.queue(video))


def stop_video():
    logger.debug('Stop current video')
    player.stop()


def next_video():
    logger.debug('Next video')
    player.next()


def play_pause_video(pause):
    player.play_pause()


def change_volume(increase):
    player.change_volume(increase)
    logger.debug('Change player volume, volume=' + str(player.volume))


def seek_time(forward, long):
    logger.debug('Seek video time, forward=%r, long=%r' % (forward, long))
    player.seek(forward, long)


def parse_playlist(url):
    ydl_opts = {
        'ignoreerrors': True,
        'extract_flat': 'in_playlist'
    }
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    with ydl:  # Download the playlist data without downloading the videos.
        data = ydl.extract_info(url, download=False)

    base_url = url.split('/playlist', 1)[0]
    urls = [base_url + '/watch?v=' + entry['id'] for entry in data['entries']]
    return urls


#stream_video("https://www.youtube.com/playlist?list=OLAK5uy_nW7BR4s8FW7r1EJCAeyB9wZxYmp4EjZX0")
