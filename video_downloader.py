import youtube_dl

from threading import Thread, Condition
from collections import deque


class VideoDownloader(object):
    def __init__(self, dl_callback):
        self.stop = False
        self.queue = deque()
        self.cv = Condition()
        self.thread = Thread(target=self.__download_queued_videos,
                             args=(dl_callback,))
        self.thread.start()

    def download(self, video):
        video['path'] = '/tmp/' + video['title'] + '.mp4'
        ydl = youtube_dl.YoutubeDL({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                      'bestvideo+bestaudio/best',
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'outtmpl': video['path']
        })
        with ydl:  # Download the video
            ydl.download([video['url']])

    def queue_downloads(self, urls):
        with self.cv:
            for url in urls:
                metadata = self.fetch_metadata(url)
                if metadata is not None:
                    self.queue.append(metadata)
            self.cv.notify()

    def __download_queued_videos(self, dl_callback):
        while not self.stop:
            with self.cv:
                while len(self.queue) == 0 and not self.stop:
                    self.cv.wait()
                if self.stop:
                    return
                video = self.queue.popleft()
                self.download(video)
                dl_callback(video)

    def fetch_metadata(self, url):
        ydl = youtube_dl.YoutubeDL(
            {
                'noplaylist': True,
                'ignoreerrors': True,
            })
        with ydl:  # Download the video data without downloading it.
            data = ydl.extract_info(url, download=False)
        if data is None:
            # NOTE log error
            return None

        return {'title': data['title'],
                'url':   url}


def make_video_downloader(dl_callback):
    downloader = VideoDownloader(dl_callback)

    return downloader
