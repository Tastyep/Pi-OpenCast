import logging.config

import structlog
from OpenCast.config import config


def init(module_name):
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
    pre_chain = [
        # Add the log level and a timestamp to the event_dict if the log entry
        # is not from structlog.
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "plain": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=False),
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processor": structlog.dev.ConsoleRenderer(colors=True),
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "colored",
                },
                "file": {
                    "level": "DEBUG",
                    "filename": "log/OpenCast.log",
                    "class": "logging.handlers.TimedRotatingFileHandler",
                    "when": "D",
                    "backupCount": 5,
                    "formatter": "plain",
                },
            },
            "loggers": {
                module_name: {
                    "handlers": ["default", "file"],
                    "level": config["log.level"],
                    "propagate": True,
                }
            },
        }
    )

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            _add_logger_name,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _add_logger_name(logger, method_name, event_dict):
    event_dict = structlog.stdlib.add_logger_name(logger, method_name, event_dict)
    logger_name = event_dict["logger"].split(".")
    short_name = ".".join(logger_name[-2:])
    event_dict["logger"] = f"{short_name: <20}"
    return event_dict
