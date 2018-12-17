import logging

from hurry.filesize import alternative, size


class DownloadLogger(object):
    def __init__(self):
        self._logger = logging.getLogger('Downloader')

    def log_download(self, d):
        if d['status'] == 'downloading':
            self._logger.debug("[downloader] {} | {} | {}"
                               .format(d['filename'],
                                       self._format_ratio(d),
                                       self._format_speed(d)))
        elif d['status'] == 'error':
            self._logger.error("[downloader] error downloading {}"
                               .format(d))
        elif d['status'] == 'finished':
            self._logger.debug("[downloader] finished downloading {}"
                               " ({})"
                               .format(d['filename'], size(d['total_bytes'])))

    def _format_ratio(self, d):
        downloaded = d['downloaded_bytes']
        total = d['total_bytes']
        if downloaded is None or total is None:
            return "unknown %"

        return "{0:.2f}%".format(100 *
                                 (d['downloaded_bytes'] / d['total_bytes']))

    def _format_speed(self, d):
        speed = d['speed']
        if d['speed'] is None:
            speed = 0

        return "{}/s".format(size(int(speed), system=alternative))
