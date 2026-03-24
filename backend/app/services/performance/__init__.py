"""Low-risk performance wrappers around existing builders.

Keep package import side effects minimal so leaf modules such as
``cache_store`` can be imported without pulling in ``home_orchestrator``.
"""

from __future__ import annotations

from typing import Any

__all__ = ["HomeOrchestrator", "HomeRequestContext", "home_orchestrator"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from .home_orchestrator import (
            HomeOrchestrator,
            HomeRequestContext,
            home_orchestrator,
        )

        exports = {
            "HomeOrchestrator": HomeOrchestrator,
            "HomeRequestContext": HomeRequestContext,
            "home_orchestrator": home_orchestrator,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
