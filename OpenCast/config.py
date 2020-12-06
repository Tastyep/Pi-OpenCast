""" The configuration module

A config object is exposed with the default values already set.
Use one of the different methods to update/retrieve its content.
"""
import collections.abc
from os import environ

import structlog
from yaml import YAMLError
from yaml import safe_load as yaml_safe_load

# fmt: off
DEFAULT_CONFIG = {
    "log": {
        "level": "INFO"
    },
    "server": {
        "host": "0.0.0.0",
        "port": 2020
    },
    "database": {
        "file": "opencast.db",
    },
    "player": {
        "loop_last": "album",
    },
    "downloader": {
        "output_directory": "/tmp",
        "max_concurrency": 3
    },
    "subtitle": {
        "enabled": True,
        "language": "eng"
    }
}
# fmt: on


class ConfigError(Exception):
    """ The base class for configuration errors. """

    pass


class ConfigContentError(ConfigError):
    """The error raised when given invalid configuration entries.

    Attributes:
        errors: A list of pairs.
                The first parameter of the pair is the configuration path.
                The second is a message description.
    """

    def __init__(self, errors: dict):
        """The config content error constructor.

        Args:
            errors: The collection of encountered errors.
                    Keys correspond to config entry paths.
        """
        self.errors = errors


class Config:
    """Configuration wrapper around a dict object.

    Configuration entries are accessible using the [] operator just like a dict.
    The main difference is that entries are read only.
    The configuration can be read from a YAML file, a dict object and the environment.
    """

    def __init__(self, content: dict, check_env=False):
        """Construct the configuration given a dict

        Args:
            content:    The default content of the configuration.
            check_env:  optional, True to import configuration from the environment,
                        False otherwise.
        """
        self._logger = structlog.get_logger(__name__)
        self._content = content
        if check_env:
            self.override_from_env(environ, prefix="OPENCAST")

    def __getitem__(self, key: str):
        """Access a configuration by keys

        Args:
            key: The key to the configuration entry.
                 key composition with a dot as separator is handled: ex: foo.bar

        Returns:
            The configuration value.
        """
        keys = key.split(".") if "." in key else [key]

        content = self._content
        for k in keys:
            content = content[k]
        if type(content) is dict:
            return Config(content, check_env=False)
        return content

    def __eq__(self, other):
        return self._content == other._content

    def load_from_file(self, path: str):
        """Loads the configuration from a YAML file.

        Args:
            path: The absolute path to the YAML file.

        Raises:
            ConfigError: When the file is unprocessable.
            ConfigContentError: For config content errors.
        """
        try:
            stream = open(path, "r")
        except Exception as e:
            self._logger.error("Can't open the configuration", error=e)
            raise ConfigError("Can't open the configuration") from e

        with stream:
            try:
                content = yaml_safe_load(stream)
            except YAMLError as e:
                self._logger.error("invalid file", error=e)
                raise ConfigError("Can't load the file's content") from e

        self.load_from_dict(content)

    def load_from_dict(self, content: dict):
        """Loads the configuration from a dict.

        Args:
            content: The object containing the overrides to apply on the configuration.

        Raises:
            ConfigContentError: For config content errors.
        """
        errors = self._validate_input(content, self._content, [])
        if errors:
            raise ConfigContentError(errors)

        self._update_content(self._content, content)

    def override_from_env(self, env: dict, prefix: str):
        """Override the existing configuration with values from the environment.

        Args:
            env: A dictionary representing the environment variables.
            prefix: The prefix identifying the environment variables.
        """

        def override_content(content, prefix):
            for k, v in content.items():
                env_key = f"{prefix}_{k}".upper()
                if type(v) is dict:
                    override_content(content[k], env_key)
                    return
                if env_key in env:
                    content[k] = type(content[k])(env[env_key])

        override_content(self._content, prefix)

    def _update_content(self, content, updates):
        for k, v in updates.items():
            if isinstance(v, collections.abc.Mapping):
                content[k] = self._update_content(content[k], v)
            else:
                content[k] = v
        return content

    def _validate_input(self, source, dest, path):
        errors = {}
        for k, v in source.items():
            if k not in dest:
                key_path = ".".join([*path, k])
                errors[key_path] = "not found"
                self._logger.error(errors[key_path], key=key_path)
                continue
            if not isinstance(v, type(dest[k])):
                key_path = ".".join([*path, k])
                errors[
                    key_path
                ] = f"type is '{type(v).__name__}' should be '{type(dest[k]).__name__}'"
                self._logger.error(errors[key_path], key=key_path)
                continue
            if type(v) is dict:
                errors = {
                    **errors,
                    **self._validate_input(source[k], dest[k], [*path, k]),
                }

        return errors


config = Config(DEFAULT_CONFIG, check_env=True)
