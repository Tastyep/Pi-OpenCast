from enum import Enum, auto

import structlog
from tinydb import TinyDB
from tinydb.storages import JSONStorage, MemoryStorage

from .facade import DataFacade


class StorageType(Enum):
    JSON = auto()
    MEMORY = auto()


class DataManager(object):
    def __init__(self, repo_factory):
        self._logger = structlog.get_logger(__name__)
        self._repo_factory = repo_factory

    def connect(self, storage: StorageType, **kwargs):
        storage = JSONStorage if storage == StorageType.JSON else MemoryStorage
        database = TinyDB(storage=storage, **kwargs)
        return DataFacade(database, self._repo_factory)
