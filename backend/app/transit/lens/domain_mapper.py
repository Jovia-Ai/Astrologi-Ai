from __future__ import annotations

from typing import Any, Dict


def enrich_marker(marker: Dict[str, Any]) -> Dict[str, Any]:
    eid = str(marker.get("event_id", "")).lower()

    if "venus" in eid:
        marker.setdefault("domains", []).append("beauty")
        marker.setdefault("domains", []).append("relationship")

    if "jupiter" in eid or "mc" in eid:
        marker.setdefault("domains", []).append("business")

    if "moon.voc" in eid:
        marker.setdefault("tags", []).append("moon_voc")

    return marker
