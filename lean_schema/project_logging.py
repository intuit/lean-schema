"""
Simple logging configuration. All log statements go to the various
handlers defined below.

"""

__author__ = "prussell"

##### STDLIB
import logging
import logging.config
import os

##### INIT AND DECLARATIONS
LOG_LEVELS = {"NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
LOG_LEVEL_ENV_VAR = "LOGGING_LEVEL"
LOGGER_NAME = os.getenv("LOGGER_NAME", "common-logger")
LOG_LEVEL = os.getenv(LOG_LEVEL_ENV_VAR, "DEBUG")
if LOG_LEVEL not in LOG_LEVELS:
    raise EnvironmentError(
        "Invalid value '{}' for env var {}, must be one of: {}".format(
            LOG_LEVEL, LOG_LEVEL_ENV_VAR, LOG_LEVELS
        )
    )
LOGGING_SETTINGS = {
    "version": 1,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d: %(message)s"
        },
        "simple": {"format": "%(levelname)s %(asctime)s %(module)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        LOGGER_NAME: {"handlers": ["console"], "level": LOG_LEVEL, "propagate": True}
    },
}

logging.config.dictConfig(LOGGING_SETTINGS)
# Actual logger object that we use to write log statements
logger = logging.getLogger(LOGGER_NAME)
