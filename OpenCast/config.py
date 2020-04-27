import yaml

import structlog


class Config:
    def __init__(self, content: dict):
        self._logger = structlog.get_logger(__name__)
        self._content = content

    def __getitem__(self, key):
        keys = key.split(".") if "." in key else [key]

        content = self._content
        for k in keys:
            content = content[k]
        if type(content) is dict:
            return Config(content)
        return content

    def load_from_file(self, path: str):
        try:
            stream = open(path, "r")
        except OSError as e:
            self._logger.error("Can't open the configuration", error=e)
            return

        with stream:
            try:
                content = yaml.safe_load(stream)
                self.load_from_dict(content)
            except yaml.YAMLError as e:
                self._logger.error("invalid file", error=e)

    def load_from_dict(self, content: dict):
        self._unpack_dict(content, self._content, [])

    def _unpack_dict(self, source, dest, path):
        for k, v in source.items():
            if k not in dest:
                self._logger.error("invalid key", key=".".join([*path, k]))
                continue
            if type(v) is dict:
                self._unpack_dict(source[k], dest[k], [*path, k])
                continue
            dest[k] = v


# fmt: off
config = Config({
    "server": {
        "host": "0.0.0.0",
        "port": 2020
    },
    "player": {
        "hide_background": True,
        "loop_last": True,
        "history_size": 15
    },
    "downloader": {
        "output_directory": "/tmp"
    },
    "subtitle": {
        "language": "eng"
    }
})
# fmt: on
