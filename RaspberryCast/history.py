import logging
import os

from .config import config

logger = logging.getLogger(__name__)
config = config['VideoPlayer']


class History(object):
    def __init__(self, items=[]):
        self._index = 0
        self._items = items
        self._browsing = False

    def __repr__(self):
        return str(self._items)

    def push(self, object):
        if object in self._items:
            return

        self.stop_browsing()
        self._items.insert(0, object)
        if len(self._items) > config.history_size:
            last_item = self._items.pop()
            file_path = str(last_item.path)

            if os.path.isfile(file_path):
                logger.info("[history] deleting {}".format(file_path))
                os.remove(file_path)
        logger.debug("[history] {}".format(self))

    def prev(self):
        pos = self._index + 1
        if pos >= len(self._items):
            return False

        self._browsing = True
        self._index = pos
        return True

    def next(self):
        if self._index is 0:
            self._browsing = False
            return False

        self._index -= 1
        self._browsing = self._index > 0
        return True

    def current_item(self):
        return self._items[self._index]

    def browsing(self):
        return self._browsing

    def stop_browsing(self):
        self._browsing = False
        self._index = 0
        logger.debug("[history] browsing turned off: {}".format(self))
