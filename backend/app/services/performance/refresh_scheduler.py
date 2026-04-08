"""Simple queue-friendly background refresh hook."""
from __future__ import annotations

import logging
import threading
from collections.abc import Callable

logger = logging.getLogger(__name__)
_MAX_ACTIVE_REFRESHES = 2
_active_refresh_names: set[str] = set()
_active_refresh_lock = threading.Lock()
_refresh_semaphore = threading.Semaphore(_MAX_ACTIVE_REFRESHES)


def schedule_home_refresh(*, name: str, task: Callable[[], None], enabled: bool) -> bool:
    if not enabled:
        return False

    with _active_refresh_lock:
        if name in _active_refresh_names:
            return False
        _active_refresh_names.add(name)

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
        with _active_refresh_lock:
            _active_refresh_names.discard(name)
        logger.exception("performance refresh schedule failed", extra={"refresh_name": name})
        return False


def _run_task(name: str, task: Callable[[], None]) -> None:
    try:
        with _refresh_semaphore:
            task()
    except Exception:  # pragma: no cover - background safety
        logger.exception("performance refresh task failed", extra={"refresh_name": name})
    finally:
        with _active_refresh_lock:
            _active_refresh_names.discard(name)
