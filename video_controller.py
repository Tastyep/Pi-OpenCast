import youtube_dl
import omxplayer

omx_player = omxplayer.make_player()


def stream_video(url, sub=False):
    omx_player.stop()

    video_path = download_video(url)
    omx_player.play(video_path)


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


# stream_video("https://www.youtube.com/playlist?list=PLlpsJiGuS_nOn6Qvl35ik4X1AN7b7WlhM")
