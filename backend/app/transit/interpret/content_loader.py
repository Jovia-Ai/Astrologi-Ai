"""Load interpretation content with caching."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

_CACHE: dict[Tuple[str, str], Dict[str, Any]] = {}


def load_content(*, lang: str = "tr", version: str = "tr.v1") -> Dict[str, Any]:
    key = (lang, version)
    if key in _CACHE:
        return _CACHE[key]

    base_path = Path(__file__).resolve().parent / "content" / lang
    content = {
        "meta": _read_json(base_path / "meta.json"),
        "rules": _read_json(base_path / "rules.json"),
        "events": _read_json(base_path / "events.json"),
        "fallbacks": _read_json(base_path / "fallbacks.json"),
    }
    _CACHE[key] = content
    return content


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
