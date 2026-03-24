"""Simple queue-friendly background refresh hook."""
from __future__ import annotations

import logging
import threading
from collections.abc import Callable

logger = logging.getLogger(__name__)


def schedule_home_refresh(*, name: str, task: Callable[[], None], enabled: bool) -> bool:
    if not enabled:
        return False

    try:
        thread = threading.Thread(
            target=_run_task,
            args=(name, task),
            name=f"home-refresh-{name}",
            daemon=True,
        )
        thread.start()
        return True
    except Exception:  # pragma: no cover - defensive guard
        logger.exception("performance refresh schedule failed", extra={"refresh_name": name})
        return False


def _run_task(name: str, task: Callable[[], None]) -> None:
    try:
        task()
    except Exception:  # pragma: no cover - background safety
        logger.exception("performance refresh task failed", extra={"refresh_name": name})
