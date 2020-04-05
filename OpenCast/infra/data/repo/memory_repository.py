from copy import deepcopy

from .context import Context
from .error import RepoError


class MemoryRepository:
    def __init__(self):
        self._table = []

    def create(self, model):
        if self.get(model.id) is not None:
            raise RepoError("cannot create: model '{}' already exists".format(model.id))
        self._table.append(model)

    def update(self, model):
        e = self.get(model.id)
        if e is None:
            raise RepoError("cannot update: model '{}' doesn't exists".format(model.id))
        if e.version > model.version:
            raise RepoError("cannot update: model '{}' is outdated".format(model.id))
        self._table = [model if e.id == model.id else e for e in self._table]

    def delete(self, id_):
        prev_size = len(self._table)
        self._table = [e for e in self._table if e.id != id_]
        if len(self._table) == prev_size:
            raise RepoError("cannot delete: model '{}' doesn't exist".format(id_))

    def list(self):
        return self._table

    def get(self, id_):
        model = next((e for e in self._table if e.id == id_), None)
        if model is None:
            return None
        return deepcopy(model)

    def make_context(self):
        return Context(self)
