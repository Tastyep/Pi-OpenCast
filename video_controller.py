import youtube_dl
import omxplayer
import video_downloader


player = omxplayer.make_player(0)
downloader = video_downloader.make_video_downloader(lambda video:
                                                    player.queue_video(video))


def stream_video(url):
    player.stop()

    if '/playlist' in url:
        urls = parse_playlist(url)
        url = urls[0]
        downloader.queue_downloads(urls[1:])
        # Change the player's state so that it automatically plays videos added
        # to its queue
        player.play()

    video = downloader.fetch_metadata(url)
    if video is None:
        return
    downloader.download(video)
    player.play(video)


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


stream_video("https://www.youtube.com/playlist?list=OLAK5uy_nW7BR4s8FW7r1EJCAeyB9wZxYmp4EjZX0")
