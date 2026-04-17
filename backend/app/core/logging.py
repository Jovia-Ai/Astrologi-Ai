"""Logging helpers for consistent formatting across the backend."""
from __future__ import annotations

import logging
import os
from logging.config import dictConfig
from pathlib import Path
from typing import Mapping


_ENABLED_ENV_VALUES = {"1", "true", "yes", "on"}


def _env_flag(name: str, default: str) -> bool:
    return os.getenv(name, default).strip().lower() in _ENABLED_ENV_VALUES


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
    timing_logger = logging.getLogger("natal.timing")
    timing_logger.setLevel(level.upper())
    timing_logger.propagate = False
    timing_logger.handlers.clear()

    # Keep timing events visible in stdout while retaining root logger behavior.
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    timing_logger.addHandler(console_handler)

    if _env_flag("ENABLE_NATAL_TIMING_FILE_SINK", "true"):
        log_path = Path(os.getenv("NATAL_TIMING_LOG_PATH", "/tmp/natal_timings.jsonl")).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        timing_logger.addHandler(file_handler)
    logging.getLogger(__name__).debug("Logging configured at %s", level)
