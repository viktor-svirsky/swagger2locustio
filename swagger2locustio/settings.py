"""Module: This module allows to configure library"""

import logging.config

API_OPERATIONS = ("get", "post", "put", "patch", "delete", "head", "options", "trace")
LOGGING_LEVELS = ("info", "debug", "warning", "error")


def config_logger(loglevel: str):
    """Function: Configure logger"""

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,
            "formatters": {"standard": {"format": "%(asctime)s [%(levelname)s] %(filename)s: %(message)s"},},
            "handlers": {
                "default": {
                    "level": loglevel,
                    "formatter": "standard",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",  # Default is stderr
                },
            },
            "loggers": {"": {"handlers": ["default"], "level": loglevel, "propagate": False},},  # root logger
        }
    )
