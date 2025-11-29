"""Logging helpers for consistent formatting across the backend."""
from __future__ import annotations

import logging
from logging.config import dictConfig
from typing import Mapping


def configure_logging(level: str = "INFO") -> None:
    """Configure global logging with a structured formatter."""

    config: Mapping[str, object] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            }
        },
        "root": {
            "level": level.upper(),
            "handlers": ["console"],
        },
    }
    dictConfig(config)
    logging.getLogger(__name__).debug("Logging configured at %s", level)
