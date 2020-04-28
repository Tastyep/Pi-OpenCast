from os import environ

import yaml

import structlog


class Config:
    def __init__(self, content: dict):
        self._logger = structlog.get_logger(__name__)
        self._content = content
        self._override_from_env(self._content, environ, ["OpenCast"])

    def __getitem__(self, key: str):
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
            return False

        with stream:
            try:
                content = yaml.safe_load(stream)
                return self.load_from_dict(content)
            except yaml.YAMLError as e:
                self._logger.error("invalid file", error=e)

        return False

    def load_from_dict(self, content: dict):
        if not self._validate_input(content, self._content, []):
            return False

        self._content.update(content)
        return True

    def _validate_input(self, source, dest, path):
        valid = True
        for k, v in source.items():
            if k not in dest:
                self._logger.error("invalid key", key=".".join([*path, k]))
                valid = False
                continue
            if type(v) is dict:
                valid &= self._validate_input(source[k], dest[k], [*path, k])
                continue
        return valid

    def _override_from_env(self, content: dict, env: dict, key: list):
        for k, v in content.items():
            env_keys = [*key, k]
            if type(v) is dict:
                self._override_from_env(content[k], env, env_keys)
                return
            env_key = "_".join(env_keys).upper()
            if env_key in env:
                content[k] = env[env_key]


# fmt: off
config = Config({
    "log": {
        "level": "DEBUG"
    },
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
