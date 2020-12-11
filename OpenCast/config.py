""" The configuration module

A config object is exposed with the default values already set.
Use one of the different methods to update/retrieve its content.
"""

from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="OPENCAST",
    settings_files=["config.yml"],
    environments=True,
    env_switcher="OPENCAST_ENV",
)

settings.validators.register(
    Validator(
        "LOG.LEVEL",
        default="INFO",
        is_in=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
    ),
    Validator("LOG.API_TRAFIC", default=False, is_in=[True, False]),
    Validator("SERVER.HOST", default="0.0.0.0"),
    Validator("SERVER.PORT", default=2020),
    Validator("DATABASE.FILE", default="opencast.db"),
    Validator("PLAYER.LOOP_LAST", default="album", is_in=[False, "track", "album"]),
    Validator("DOWNLOADER.OUTPUT_DIRECTORY", must_exist=True),
    Validator("DOWNLOADER.MAX_CONCURRENCY", default=3, gt=0, lt=10),
    Validator("SUBTITLE.ENABLED", default=True, is_in=[True, False]),
    Validator("SUBTITLE.LANGUAGE", default="eng", len_eq=3),
)
