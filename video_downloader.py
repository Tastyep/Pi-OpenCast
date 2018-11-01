import youtube_dl

from threading import Thread, Condition
from collections import deque


class VideoDownloader(object):
    def __init__(self, dl_callback):
        self.stopped = False
        self.queue = deque()
        self.cv = Condition()
        self.thread = Thread(target=self.__download_queued_videos,
                             args=(dl_callback,))
        self.thread.start()

    def __del__(self, dl_callback):
        with self.cv:
            self.stopped = True
            self.cv.notifyAll()
        self.thread.join()

    def download(self, video, dl_callback):
        video.path = '/tmp/' + video.title + '.mp4'
        ydl = youtube_dl.YoutubeDL({
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                      'bestvideo+bestaudio/best',
            'noplaylist': True,
            'ignoreerrors': True,
            'merge_output_format': 'mp4',
            'outtmpl': video.path
        })
        with ydl:  # Download the video
            ydl.download([video.url])
        dl_callback(video)

    def queue_downloads(self, videos):
        Thread(target=self.__queue_downloads,
               args=(videos,)).start()

    def list_queue(self):
        return list(self.queue)

    def fetch_metadata(self, video):
        ydl = youtube_dl.YoutubeDL(
            {
                'noplaylist': True,
                'ignoreerrors': True,
            })
        with ydl:  # Download the video data without downloading it.
            data = ydl.extract_info(video.url, download=False)
        video.title = data['title']

        return data is not None

    def __queue_downloads(self, videos):
        with self.cv:
            for video in videos:
                if self.fetch_metadata(video):
                    self.queue.append(video)
            self.cv.notify()

    def __download_queued_videos(self, dl_callback):
        while not self.stopped:
            with self.cv:
                while len(self.queue) == 0 and not self.stopped:
                    self.cv.wait()
                if self.stopped:
                    return
                video = self.queue.popleft()
            self.download(video, dl_callback)


def make_video_downloader(dl_callback):
    downloader = VideoDownloader(dl_callback)

    return downloader
