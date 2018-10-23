import youtube_dl
import omxplayer

omx_player = omxplayer.make_player()


def stream_video(url, sub=False):
    omx_player.stop()

    if '/playlist' in url:
        urls = parse_playlist(url)
        url = urls[0]
        add_urls_to_queue(urls[1:])

    video_path = download_video(url)
    omx_player.play(video_path)


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


def download_video(url):
    video_path = '/tmp/1.mp4'
    ydl = youtube_dl.YoutubeDL({
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                  'bestvideo+bestaudio/best',
        'ignoreerrors': True,
        'merge_output_format': 'mp4',
        'outtmpl': video_path
    })
    with ydl:  # Download the video
        ydl.download([url])

    return video_path


def add_urls_to_queue(urls):
    for url in urls:
        print("url= ", url)


stream_video("https://www.youtube.com/playlist?list=PLlpsJiGuS_nOn6Qvl35ik4X1AN7b7WlhM")
