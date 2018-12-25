import logging

from hurry.filesize import (
    alternative,
    size,
)


class DownloadLogger(object):
    def __init__(self):
        self._logger = logging.getLogger('Downloader')

    def is_enabled_for(self, level):
        return self._logger.isEnabledFor(level)

    def log_download(self, d):
        status = d.get('status', 'N/A')
        if status is 'downloading':
            self._log_download_info(d)
        elif status is 'error':
            self._log_download_error(d)
        elif status is 'finished':
            self._log_download_finished(d)

    def _log_download_info(self, d):
        filename = d.get('filename', 'unknown')
        self._logger.info("[downloader] {} | {} | {}"
                          .format(filename,
                                  self._format_ratio(d),
                                  self._format_speed(d)))

    def _log_download_error(self, d):
        filename = d.get('filename', 'unknown')
        self._logger.error("[downloader] error downloading {}: {}"
                           .format(filename, d))

    def _log_download_finished(self, d):
        filename = d.get('filename', 'unknown')
        total = d.get('total_bytes', 0)
        self._logger.info("[downloader] finished downloading {} ({})"
                          .format(filename, size(total)))

    def _format_ratio(self, d):
        downloaded = d.get('downloaded_bytes', None)
        total = d.get('total_bytes', None)
        if downloaded is None or total is None:
            return "N/A %"

        return "{0:.2f}%".format(100 * (downloaded / total))

    def _format_speed(self, d):
        speed = d.get('speed', 0)
        return "{}/s".format(size(int(speed), system=alternative))
