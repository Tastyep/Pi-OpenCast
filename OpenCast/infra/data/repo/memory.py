from copy import deepcopy

from .context import Context
from .error import RepoError


class MemoryRepo:
    def __init__(self):
        self._table = []

    def create(self, model):
        if self.get(model.id) is not None:
            raise RepoError(f"cannot create: '{model}' already exists")
        self._table.append(deepcopy(model))

    def update(self, model):
        e = self.get(model.id)
        if e is None:
            raise RepoError(f"cannot update: '{model}' doesn't exist")
        if model.version < e.version:
            raise RepoError(f"cannot update: '{model}' is outdated")

        model.update_version()
        self._table = [model if e == model else e for e in self._table]

    def delete(self, model):
        prev_size = len(self._table)
        self._table = [e for e in self._table if e != model]
        if len(self._table) == prev_size:
            raise RepoError(f"cannot delete: '{model}' doesn't exist")

    def list(self):
        return deepcopy(self._table)

    def get(self, id_):
        model = next((e for e in self._table if e.id == id_), None)
        if model is None:
            return None
        return deepcopy(model)

    def exists(self, id_):
        return next((e for e in self._table if e.id == id_), None) is not None

    def make_context(self):
        return Context(self)
