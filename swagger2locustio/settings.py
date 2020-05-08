"""Module: This module allows to configure library"""

import coloredlogs

API_OPERATIONS = ("get", "post", "put", "patch", "delete", "head", "options", "trace")
LOGGING_LEVELS = ("info", "debug", "warning", "error")


def config_logger(loglevel: str = "DEBUG"):
    """Function: Configure logger"""

    coloredlogs.install(level=loglevel, fmt="%(asctime)s [%(levelname)s] %(filename)s: %(message)s")
