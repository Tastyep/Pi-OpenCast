import logging
import os

from .config import config

logger = logging.getLogger(__name__)
config = config['VideoPlayer']


class History(object):
    def __init__(self, items=[]):
        self._index = 0
        self._browsing = False
        self._items = items

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

    def remove(self, object):
        if object not in self._items:
            return False

        index = self._items.index(object)
        if self._index >= index and self._index is not 0:
            self._index -= 1

        self._items.remove(object)
        if self.size() is 0:
            self.stop_browsing()

        return True

    def size(self):
        return len(self._items)

    def index(self):
        return self._index

    def prev(self):
        step = int(self._browsing)
        pos = self._index + step
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
        return True

    def can_prev(self):
        return self._index + int(self._browsing) < len(self._items)

    def current_item(self):
        return self._items[self._index]

    def browsing(self):
        return self._browsing

    def stop_browsing(self):
        self._index = 0
        self._browsing = False
        logger.debug("[history] browsing turned off: {}".format(self))
