import os
import logging

from .config import config

logger = logging.getLogger(__name__)
config = config["VideoPlayer"]


class History(list):
    def push(self, object):
        self.insert(0, object)
        if len(self) > config.history_size:
            last_item = self.pop()
            file_path = str(last_item.path)

            if os.path.isfile(file_path):
                logger.debug('[history] deleting {}'.format(file_path))
                os.remove(file_path)
