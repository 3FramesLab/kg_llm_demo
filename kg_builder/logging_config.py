"""
Logging configuration for uvicorn that works on Windows.
Features:
- Console output (stderr) for real-time monitoring
- Daily rotating file logs in logs/ folder
- Separate files for different log types (app, error, access)
- Async-safe with QueueHandler
- 30 days of log retention
- UTF-8 encoding for Windows compatibility
"""
import os
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "format": "%(asctime)s - %(levelname)s - %(client_addr)s - %(request_line)s - %(status_code)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        # Console handlers (for terminal output)
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "console_access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },

        # File handlers with daily rotation
        "file_app": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "app.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,  # Keep 30 days
            "encoding": "utf-8",
            "delay": False,
        },
        "file_error": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "error.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
            "level": "ERROR",
            "delay": False,
        },
        "file_access": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "access",
            "filename": str(LOGS_DIR / "access.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
            "delay": False,
        },
        "file_sql": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "detailed",
            "filename": str(LOGS_DIR / "sql.log"),
            "when": "midnight",
            "interval": 1,
            "backupCount": 30,
            "encoding": "utf-8",
            "delay": False,
        },

        # Queue handler for async-safe logging
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "queue": {
                "()": "queue.Queue",
                "maxsize": 1000,
            },
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file_app", "file_error"],
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console", "file_app"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console_access", "file_access"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services": {
            "handlers": ["console", "file_app", "file_error"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.nl_query_executor": {
            "handlers": ["console", "file_app", "file_sql"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.nl_sql_generator": {
            "handlers": ["console", "file_app", "file_sql"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.nl_query_parser": {
            "handlers": ["console", "file_app", "file_sql"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.landing_db_connector": {
            "handlers": ["console", "file_app", "file_sql"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.kpi_executor": {
            "handlers": ["console", "file_app", "file_sql"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.landing_kpi_executor": {
            "handlers": ["console", "file_app", "file_sql"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
