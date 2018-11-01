import logging
import youtube_dl
import media_player
import video_downloader

from video import Video

logger = logging.getLogger("App")
player = media_player.make_player(0)
downloader = video_downloader.make_video_downloader(lambda video:
                                                    player.queue_video(video))


def stream_video(url):
    logger.debug('stream video, URL="' + url + '"')
    player.stop()

    video = Video(url)
    if video.is_local():
        player.play(video)
        return

    if '/playlist' in url:
        urls = parse_playlist(url)
        videos = [Video(u) for u in urls]
        video = videos[0]
        logger.debug("Playlist url unwound to %r" % (videos))
        # NOTE pass on_download callback here.
        downloader.queue_downloads(videos[1:])
        # Change the player's state so that it automatically plays videos added
        # to its queue
        player.play()

    if not downloader.fetch_metadata(video):
        return

    downloader.download(video,
                        lambda video: player.play(video))


def queue_video(url):
    logger.debug('queue video, URL="' + url + '"')

    if '/playlist' in url:
        urls = parse_playlist(url)
        logger.debug("Playlist url unwound to %r" % (urls))
        downloader.queue_downloads(urls)
    else:
        downloader.queue_downloads([url])


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
