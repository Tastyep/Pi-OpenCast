""" Channels represent a pipe in which data can be transfered """

from janus import Queue


class JanusChannel:
    def __init__(self):
        self._queue = Queue()

    def send(self, item):
        self._queue.sync_q.put_nowait(item)

    async def receive(self):
        return await self._queue.async_q.get()
