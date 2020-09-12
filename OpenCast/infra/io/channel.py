""" Channels represent a pipe in which data can be transfered """

from asyncio import sleep
from queue import SimpleQueue

from janus import Queue


class PollingChannel:
    def __init__(self):
        self._queue = SimpleQueue()

    def send(self, item):
        self._queue.put(item)

    async def receive(self):
        while True:
            if not self._queue.empty():
                return self._queue.get()
            await sleep(1)


class JanusChannel:
    def __init__(self):
        self._queue = Queue()

    def send(self, item):
        self._queue.sync_q.put_nowait(item)

    async def receive(self):
        return await self._queue.async_q.get()
