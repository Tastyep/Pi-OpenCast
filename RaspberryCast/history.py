import os
import logging

from .config import config

logger = logging.getLogger(__name__)
config = config["VideoPlayer"]


class History(list):
    def __init__(self):
        self._index = 0
        self._browsing = False

    def push(self, object):
        if object in self:
            return

        self.stop_browsing()
        self.insert(0, object)
        if len(self) > config.history_size:
            last_item = self.pop()
            file_path = str(last_item.path)

            if os.path.isfile(file_path):
                logger.info('[history] deleting {}'.format(file_path))
                os.remove(file_path)
        logger.debug("[history] {}".format(self))

    def prev(self):
        pos = self._index + 1
        if len(self) <= pos:
            return False

        self._browsing = True
        self._index = pos
        return True

    def next(self):
        if self._index == 0:
            self._browsing = False
            return False

        self._index -= 1
        return True

    def current_item(self):
        return self[self._index]

    def browsing(self):
        return self._browsing

    def stop_browsing(self):
        self._browsing = False
        if self._index > 1:
            # Reverse the browsed history
            self = reversed(self[:self._index + 1]) + self[self._index + 1:]
        self._index = 0
        logger.debug("[history] browsing turned off: {}".format(self))
