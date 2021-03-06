""" Abstraction of a repository """

from typing import List

from tinydb import where

from OpenCast.infra import Id

from .context import Context
from .error import RepoError


class Repository:
    def __init__(self, database, db_lock, entity):
        self._db = database
        self._lock = db_lock
        self._entity = entity
        self._collection = database.table(entity.__name__)

    def create(self, entity):
        with self._lock:
            if self.exists(entity.id):
                raise RepoError(f"cannot create: '{entity}' already exists")

            self._collection.insert(entity.to_dict())

    def update(self, entity):
        with self._lock:
            e = self.get(entity.id)
            if e is None:
                raise RepoError(f"cannot update: '{entity}' doesn't exist")

            self._collection.update(entity.to_dict(), where("id") == str(entity.id))

    def delete(self, entity):
        with self._lock:
            self._collection.remove(where("id") == str(entity.id))

    def list(self, ids: List[Id] = None):
        with self._lock:
            if ids is None:
                results = self._collection.all()
            else:
                results = self._collection.search(
                    lambda entity: Id(entity["id"]) in ids
                )
                results.sort(key=lambda entity: ids.index(Id(entity["id"])))

        return [self._entity.from_dict(result) for result in results]

    def get(self, id_: Id):
        with self._lock:
            results = self._collection.search(where("id") == str(id_))
        return None if not results else self._entity.from_dict(results[0])

    def exists(self, id_: Id):
        with self._lock:
            return self.get(id_) is not None

    def make_context(self):
        return Context(self)
