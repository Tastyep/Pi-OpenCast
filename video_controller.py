import logging
import youtube_dl
import media_player
import video_downloader
import uuid

from video import Video

logger = logging.getLogger("App")
player = media_player.make_player(1.0)
downloader = video_downloader.make_video_downloader()


class VideoController(object):
    def stream_video(self, url):
        logger.debug('stream video, URL="' + url + '"')
        player.stop()

        video = Video(url)
        if video.is_local():
            player.play(video)
            return

        self._queue_video(video, self._play_video, first=True)

    def queue_video(self, url):
        logger.debug('queue video, URL="' + url + '"')
        self._queue_video(Video(url), player.queue, first=False)

    def stop_video(self):
        logger.debug('Stop current video')
        player.stop()

    def next_video(self):
        logger.debug('Next video')
        player.next()

    def play_pause_video(self, pause):
        player.play_pause()

    def change_volume(self, increase):
        player.change_volume(increase)
        logger.debug('Change player volume, volume=' + str(player.volume))

    def seek_time(self, forward, long):
        logger.debug('Seek video time, forward=%r, long=%r' % (forward, long))
        player.seek(forward, long)

    # Getter methods

    def list_queued_videos(self):
        videos = player.get_queue()
        videos.extend(downloader.get_queue())

        return videos

    # Private methods

    def _play_video(self, video):
        player.queue(video, first=True)
        player.play()

    def _queue_video(self, video, dl_callback, first):
        if '/playlist' in video.url:
            # Generate a unique ID for the playlist
            playlistId = uuid.uuid4()
            urls = self._parse_playlist(video.url)
            videos = [Video(u, playlistId) for u in urls]
            logger.debug("Playlist url unwound to %r" % (videos))
            downloader.queue(videos, dl_callback, first)
        else:
            downloader.queue([video], dl_callback, first)

    def _parse_playlist(self, url):
        ydl_opts = {
            'ignoreerrors': True,
            'extract_flat': 'in_playlist'
        }
        ydl = youtube_dl.YoutubeDL(ydl_opts)
        with ydl:  # Download the playlist data without downloading the videos.
            data = ydl.extract_info(url, download=False)

        base_url = url.split('/playlist', 1)[0]
        urls = [base_url + '/watch?v=' + entry['id']
                for entry in data['entries']]
        return urls


def make_video_controller():
    return VideoController()
