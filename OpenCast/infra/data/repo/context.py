class Context:
    def __init__(self, repo):
        self._repo = repo
        self._transactions = []

    def add(self, entity):
        self._transactions.append((entity, self._repo.create))

    def update(self, entity):
        self._transactions.append((entity, self._repo.update))

    def delete(self, entity):
        self._transactions.append((entity, self._repo.delete))

    def commit(self):
        entities = []
        for entity, transaction in self._transactions:
            transaction(entity)
            entities.append(entity)

        return entities
