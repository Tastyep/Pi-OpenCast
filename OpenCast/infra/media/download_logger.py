""" Logger displaying download progress """

from hurry.filesize import alternative, size


class DownloadLogger:
    def __init__(self, logger):
        self._logger = logger

    def is_enabled_for(self, level):
        return False
        # return self._logger.isEnabledFor(level)

    def log_download_progress(self, d):
        status = d.get("status", "N/A")
        if status not in ["downloading", "error", "finished"]:
            return

        getattr(self, f"_log_{status}")(d)

    def _log_downloading(self, d):
        filename = d.get("filename", "unknown")
        self._logger.info(
            "Downloading",
            filename=filename,
            ratio=self._format_ratio(d),
            speed=self._format_speed(d),
        )

    def _log_error(self, d):
        filename = d.get("filename", "unknown")
        self._logger.error("Error downloading", filename=filename, error=d)

    def _log_finished(self, d):
        filename = d.get("filename", "unknown")
        total = d.get("total_bytes", 0)
        self._logger.info(
            "Finished downloading",
            filename=filename,
            size=size(total, system=alternative),
        )

    def _format_ratio(self, d):
        downloaded = d.get("downloaded_bytes", None)
        total = d.get("total_bytes", None)
        if downloaded is None or total is None:
            return "N/A %"

        return "{0:.2f}%".format(100 * (downloaded / total))

    def _format_speed(self, d):
        speed = d.get("speed", 0)
        if speed is None:
            speed = 0
        return "{}/s".format(size(speed, system=alternative))
