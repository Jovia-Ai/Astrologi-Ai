from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Dict, List, Mapping, Sequence

DOMAIN_BY_HOUSE = {
    1: "identity",
    3: "mind",
    4: "home",
    6: "mind",
    7: "relationships",
    8: "inner",
    9: "mind",
    10: "career",
    11: "career",
    12: "inner",
}


def build_period_coverage(
    events_unscored: Sequence[Mapping[str, Any]],
    selected_ids: set[str],
    now_date: str,
    tz: str,
) -> Dict[str, Any]:
    typed = [item for item in events_unscored if isinstance(item, Mapping)]
    counts = Counter(str(item.get("bucket") or "").lower() for item in typed)
    total = len(typed)

    top_long = _top_bucket(typed, "long", limit=8)
    top_medium = _top_bucket(typed, "medium", limit=6)
    top_short = _top_bucket(typed, "short", limit=10)

    by_domain: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for item in typed:
        domain = _map_domain(item)
        by_domain[domain].append(item)

    domain_coverage: Dict[str, Dict[str, Any]] = {}
    for domain in ("identity", "relationships", "mind", "career", "home", "inner"):
        events = by_domain.get(domain, [])
        events_sorted = sorted(events, key=lambda x: (-_strength(x), str(x.get("event_id") or "")))
        domain_coverage[domain] = {
            "hits": len(events),
            "top_event_ids": [str(item.get("event_id") or "") for item in events_sorted[:5]],
        }

    skipped_due_to_dedup = _infer_skipped(typed, selected_ids)

    return {
        "counts": {
            "total": total,
            "long": int(counts.get("long", 0)),
            "medium": int(counts.get("medium", 0)),
            "short": int(counts.get("short", 0)),
        },
        "top_long": top_long,
        "top_medium": top_medium,
        "top_short": top_short,
        "domain_coverage": domain_coverage,
        "skipped_due_to_dedup": skipped_due_to_dedup,
        "notes": [
            "selection_mode=coverage_first_v1",
            f"now_date={now_date}",
            f"tz={tz}",
            f"max_cards={len(selected_ids)}",
        ],
    }


def _map_domain(item: Mapping[str, Any]) -> str:
    scope = str(item.get("scope") or "")
    point = str(item.get("natal_point") or "").upper()
    if scope == "transit_to_angles":
        if point == "ASC":
            return "identity"
        if point == "DSC":
            return "relationships"
        if point == "MC":
            return "career"
        if point == "IC":
            return "home"

    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    raw_house = houses.get("natal_point_house")
    try:
        house = int(raw_house) if raw_house is not None else None
    except (TypeError, ValueError):
        house = None
    if isinstance(house, int):
        return DOMAIN_BY_HOUSE.get(house, "identity")

    tags = [str(x).lower() for x in (item.get("tags") or []) if str(x).strip()]
    if "relationships" in tags:
        return "relationships"
    if "career" in tags:
        return "career"
    return "identity"


def _top_bucket(items: Sequence[Mapping[str, Any]], bucket: str, limit: int) -> List[Dict[str, Any]]:
    filtered = [item for item in items if str(item.get("bucket") or "").lower() == bucket]
    filtered.sort(key=lambda item: (-_strength(item), str(item.get("event_id") or "")))
    out: List[Dict[str, Any]] = []
    for item in filtered[:limit]:
        out.append(
            {
                "event_id": str(item.get("event_id") or ""),
                "label": str(item.get("label") or ""),
                "strength": _strength(item),
                "orb_deg": _safe_float(item.get("orb_deg"), 0.0),
                "phase": str(item.get("phase") or ""),
                "transit_body": str(item.get("transit_body") or ""),
                "aspect": str(item.get("aspect") or ""),
                "natal_point": str(item.get("natal_point") or ""),
                "houses": dict(item.get("houses") or {}) if isinstance(item.get("houses"), Mapping) else {},
                "bucket": str(item.get("bucket") or ""),
            }
        )
    return out


def _infer_skipped(items: Sequence[Mapping[str, Any]], selected_ids: set[str]) -> List[Dict[str, Any]]:
    selected_items = [item for item in items if str(item.get("event_id") or "") in selected_ids]
    selected_sig = {
        (
            str(item.get("transit_body") or "").lower(),
            str(item.get("aspect") or "").lower(),
            str(item.get("natal_point") or "").upper(),
        ): str(item.get("event_id") or "")
        for item in selected_items
    }
    body_counts = Counter(str(item.get("transit_body") or "").lower() for item in selected_items)
    house_counts = Counter(_house(item) for item in selected_items if _house(item) is not None)

    skipped: List[Dict[str, Any]] = []
    for item in items:
        eid = str(item.get("event_id") or "")
        if not eid or eid in selected_ids:
            continue
        reason = "low_strength"
        dupe_of = None
        sig = (
            str(item.get("transit_body") or "").lower(),
            str(item.get("aspect") or "").lower(),
            str(item.get("natal_point") or "").upper(),
        )
        if sig in selected_sig:
            reason = "duplicate_signature"
            dupe_of = selected_sig[sig]
        else:
            body = str(item.get("transit_body") or "").lower()
            if body_counts[body] >= 2:
                reason = "same_transit_stack"
            house = _house(item)
            if house is not None and house_counts[house] >= 2:
                reason = "same_house_overflow"
        skipped.append({"event_id": eid, "reason": reason, "dupe_of": dupe_of})
        if len(skipped) >= 40:
            break
    return skipped


def _house(item: Mapping[str, Any]) -> int | None:
    houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
    raw = houses.get("natal_point_house")
    try:
        return int(raw) if raw is not None else None
    except (TypeError, ValueError):
        return None


def _strength(item: Mapping[str, Any]) -> float:
    return _safe_float(item.get("strength"), 0.0)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
