import logging
import youtube_dl
import media_player
import video_downloader

logger = logging.getLogger("App")
player = media_player.make_player(0)
downloader = video_downloader.make_video_downloader(lambda video:
                                                    player.queue_video(video))


def stream_video(url):
    logger.debug('stream_video, URL="' + url + '"')
    player.stop()

    if '/playlist' in url:
        urls = parse_playlist(url)
        url = urls[0]
        logger.debug("Playlist url unwound to %r" % (urls))
        downloader.queue_downloads(urls[1:])
        # Change the player's state so that it automatically plays videos added
        # to its queue
        player.play()

    video = downloader.fetch_metadata(url)
    if video is None:
        return

    downloader.download(video,
                        lambda video: player.play(video))


def stop_video():
    logger.debug('Stop current video')
    player.stop()


def next_video():
    logger.debug('Next video')
    player.next()


def pause_video(pause):
    if pause:
        player.pause()
    else:
        player.start()


def change_volume(increase):
    player.change_volume(increase)
    logger.debug('Change player volume, volume=' + str(player.volume()))


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
