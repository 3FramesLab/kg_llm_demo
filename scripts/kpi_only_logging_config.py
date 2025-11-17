"""
Optional: KPI-Only Console Logging Configuration
Use this if you want to see ONLY KPI execution logs in your console.
"""

# Add this to your logging_config.py if you want KPI-only console output

KPI_ONLY_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "kpi_format": {
            "format": "%(asctime)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "kpi_console": {
            "formatter": "kpi_format",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # Only show KPI-related logs in console
        "kg_builder.routes": {
            "handlers": ["kpi_console"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.landing_kpi_service_jdbc": {
            "handlers": ["kpi_console"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.landing_kpi_executor": {
            "handlers": ["kpi_console"],
            "level": "INFO",
            "propagate": False,
        },
        "kg_builder.services.nl_query_executor": {
            "handlers": ["kpi_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Usage: Replace LOGGING_CONFIG with KPI_ONLY_LOGGING_CONFIG in main.py
# logging.config.dictConfig(KPI_ONLY_LOGGING_CONFIG)
