"""Proxy package to expose backend.app as top-level 'app'."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_backend_app_dir = Path(__file__).resolve().parents[1] / "backend" / "app"
_backend_init = _backend_app_dir / "__init__.py"

if not _backend_init.exists():
    raise ImportError(f"Cannot locate backend/app package at {_backend_app_dir}")

current_module = sys.modules[__name__]
current_module.__file__ = str(_backend_init)
current_module.__path__ = [str(_backend_app_dir)]

spec = importlib.util.spec_from_file_location(__name__, _backend_init)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(current_module)
