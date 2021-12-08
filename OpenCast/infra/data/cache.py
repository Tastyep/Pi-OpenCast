""" Data caching module """


from dataclasses import dataclass
from datetime import datetime, timedelta


class TimeBasedCache:
    @dataclass
    class TimeBasedData:
        data: dict
        creation_time: datetime

    def __init__(self, max_duration: timedelta) -> None:
        self._max_duration = max_duration
        self._cache = {}

    def get(self, key: str):
        print(f"CACHE {key} {self._cache}")
        entry = self._cache.get(key)
        if entry is None:
            return entry
        return entry.data

    def register(self, key: str, data):
        self._cache[key] = self.TimeBasedData(data, datetime.now())

    def clean(self):
        now = datetime.now()
        for key in list(self._cache.keys()):
            if now - self._cache[key].creation_time > self._max_duration:
                print(f"REMOVE {key}")
                del self._cache[key]
