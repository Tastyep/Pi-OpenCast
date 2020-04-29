from os import environ

import yaml

import structlog


class ConfigError(Exception):
    pass


class ConfigContentError(ConfigError):
    def __init__(self, errors: list):
        self.errors = errors


class Config:
    def __init__(self, content: dict, check_env=False):
        self._logger = structlog.get_logger(__name__)
        self._content = content
        if check_env:
            self._override_from_env(self._content, environ, ["OpenCast"])

    def __getitem__(self, key: str):
        keys = key.split(".") if "." in key else [key]

        content = self._content
        for k in keys:
            content = content[k]
        if type(content) is dict:
            return Config(content, check_env=False)
        return content

    def load_from_file(self, path: str):
        try:
            stream = open(path, "r")
        except OSError as e:
            self._logger.error("Can't open the configuration", error=e)
            raise ConfigError("Can't open the configuration") from e

        with stream:
            try:
                content = yaml.safe_load(stream)
                self.load_from_dict(content)
            except yaml.YAMLError as e:
                self._logger.error("invalid file", error=e)
                raise ConfigError("Can't load the file's content") from e

    def load_from_dict(self, content: dict):
        errors = self._validate_input(content, self._content, [])
        if errors:
            raise ConfigContentError(errors)

        self._content.update(content)

    def _validate_input(self, source, dest, path):
        errors = []
        for k, v in source.items():
            if k not in dest:
                errors.append((".".join([*path, k]), "not found"))
                self._logger.error(errors[-1][1], key=errors[-1][0])
                continue
            if not isinstance(v, type(dest[k])):
                errors.append(
                    (
                        ".".join([*path, k]),
                        f"type is '{type(v).__name__}' should be '{type(dest[k]).__name__}'",
                    )
                )
                self._logger.error(errors[-1][1], key=errors[-1][0])
                continue
            if type(v) is dict:
                errors = [
                    *errors,
                    *self._validate_input(source[k], dest[k], [*path, k]),
                ]

        return errors

    def _override_from_env(self, content: dict, env: dict, key: list):
        for k, v in content.items():
            env_keys = [*key, k]
            if type(v) is dict:
                self._override_from_env(content[k], env, env_keys)
                return
            env_key = "_".join(env_keys).upper()
            if env_key in env:
                content[k] = type(content[k])(env[env_key])


# fmt: off
config = Config({
    "log": {
        "level": "INFO"
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
}, check_env=True)
# fmt: on
