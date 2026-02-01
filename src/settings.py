import os
import logging
import logging.config

DEBUG = os.environ.get("DEBUG", '').lower()

DEBUG_LOG_FILE = os.environ.get("DEBUG_LOG_FILE", '').strip() or "./logs/debug.log"
INFO_LOG_FILE = os.environ.get("INFO_LOG_FILE", '').strip() or "./logs/info.log"
ERROR_LOG_FILE = os.environ.get("ERROR_LOG_FILE", '').strip() or "./logs/error.log"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": DEBUG_LOG_FILE,
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": INFO_LOG_FILE,
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": ERROR_LOG_FILE,
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },

    "loggers": {
        "my_module": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": False
        }
    },

    "root": {
        "level": "INFO" if DEBUG else "INFO",
        "handlers": ["console", "info_file_handler", "error_file_handler"]
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

