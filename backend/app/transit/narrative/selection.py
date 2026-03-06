from __future__ import annotations

from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from app.transit.narrative.hybrid_context import build_hybrid_event_context
from app.transit.narrative.point_policy import is_public_event, point_weight

ANGLE_PRIORITY = {"ASC": 0, "DSC": 1, "MC": 2, "IC": 3}
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
OUTER_STACK = {"uranus", "pluto"}
PHASE_BOOST = {"exact": 1.0, "exactish": 0.95, "applying": 0.9, "separating": 0.72}
BUCKET_BOOST = {"long": 1.0, "medium": 0.75, "short": 0.45}


def select_event_ids(
    events: Sequence[Mapping[str, Any]],
    max_cards: int = 5,
    natal: Mapping[str, Any] | None = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    typed = [dict(item) for item in events if isinstance(item, Mapping)]
    typed = [item for item in typed if _is_public_allowed(item)]
    if not typed or max_cards <= 0:
        return [], {"selection_mode": "coverage_first_v1", "selected_ids": [], "reasons": {}, "skipped_due_to_dedup": []}

    selected: List[Dict[str, Any]] = []
    reasons: Dict[str, List[str]] = {}
    skipped: List[Dict[str, Any]] = []

    signature_seen: Dict[Tuple[str, str, str], str] = {}
    cluster_seen: Dict[str, str] = {}
    body_counts: Counter[str] = Counter()
    house_counts: Counter[int] = Counter()
    covered_domains = set()
    hybrid_cache: Dict[str, Dict[str, Any]] = {}
    salience_map: Dict[str, float] = {}

    def _event_id(item: Mapping[str, Any]) -> str:
        return str(item.get("event_id") or "")

    def _signature_key(item: Mapping[str, Any]) -> Tuple[str, str, str]:
        return (
            str(item.get("transit_body") or "").lower(),
            str(item.get("aspect") or "").lower(),
            str(item.get("natal_point") or "").upper(),
        )

    def _house(item: Mapping[str, Any]) -> int | None:
        houses = item.get("houses") if isinstance(item.get("houses"), Mapping) else {}
        raw = houses.get("natal_point_house")
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    def _strength(item: Mapping[str, Any]) -> float:
        try:
            return float(item.get("strength"))
        except (TypeError, ValueError):
            return 0.0

    def _orb(item: Mapping[str, Any]) -> float:
        try:
            return float(item.get("orb_deg"))
        except (TypeError, ValueError):
            return 9.9

    def _hybrid(item: Mapping[str, Any]) -> Dict[str, Any]:
        eid = _event_id(item)
        if eid not in hybrid_cache:
            hybrid_cache[eid] = build_hybrid_event_context(item, natal or {}, natal_promise={})
        return hybrid_cache[eid]

    def _target_house(item: Mapping[str, Any]) -> int | None:
        hybrid = _hybrid(item)
        pack = hybrid.get("natal_context_pack") if isinstance(hybrid.get("natal_context_pack"), Mapping) else {}
        target = pack.get("target") if isinstance(pack.get("target"), Mapping) else {}
        raw = target.get("house")
        try:
            return int(raw) if raw is not None else None
        except (TypeError, ValueError):
            return None

    def _domain(item: Mapping[str, Any]) -> str:
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
        house = _house(item)
        if isinstance(house, int):
            return DOMAIN_BY_HOUSE.get(house, "identity")
        tags = [str(x).lower() for x in (item.get("tags") or []) if str(x).strip()]
        if "relationships" in tags:
            return "relationships"
        if "career" in tags:
            return "career"
        if "inner" in tags:
            return "inner"
        return "identity"

    def _cluster_key(item: Mapping[str, Any]) -> str:
        body = str(item.get("transit_body") or "").lower()
        aspect = str(item.get("aspect") or "").lower()
        target_house = _target_house(item)
        if target_house in {1, 3, 7, 9, 10}:
            house_key = str(target_house)
        else:
            natal_house = _house(item)
            house_key = str(natal_house) if isinstance(natal_house, int) else "na"
        return f"{body}|{aspect}|h{house_key}"

    def _salience(item: Mapping[str, Any]) -> float:
        strength = max(0.0, min(1.0, _strength(item)))
        orb = _orb(item)
        orb_signal = max(0.0, min(1.0, 1.0 - (orb / 6.0)))
        phase = PHASE_BOOST.get(str(item.get("phase") or "").lower(), 0.65)
        bucket = BUCKET_BOOST.get(str(item.get("bucket") or "").lower(), 0.5)
        angle_hit = 1.0 if str(item.get("scope") or "") == "transit_to_angles" else 0.0
        transit_body = str(item.get("transit_body") or "").lower()
        outer = 1.0 if transit_body in OUTER_STACK else 0.0
        mind_hit = 1.0 if (_house(item) in {3, 9} or _target_house(item) in {3, 9}) else 0.0
        policy_weight = min(
            1.0,
            0.5 * point_weight(item.get("transit_body")) + 0.5 * point_weight(item.get("natal_point")),
        )
        score = (
            0.55 * strength
            + 0.15 * orb_signal
            + 0.12 * phase
            + 0.08 * bucket
            + 0.05 * angle_hit
            + 0.03 * outer
            + 0.02 * mind_hit
        )
        return round(min(1.0, max(0.0, score * policy_weight)), 4)

    def _can_add(item: Mapping[str, Any]) -> Tuple[bool, str, str | None]:
        eid = _event_id(item)
        sig = _signature_key(item)
        if sig in signature_seen:
            return False, "duplicate_signature", signature_seen[sig]
        cluster = _cluster_key(item)
        if cluster in cluster_seen:
            return False, "cluster_collision", cluster_seen[cluster]
        body = str(item.get("transit_body") or "").lower()
        point = str(item.get("natal_point") or "").upper()
        if body_counts[body] >= 2:
            if not (_strength(item) >= 0.95 and any(str(x.get("natal_point") or "").upper() != point for x in selected if str(x.get("transit_body") or "").lower() == body)):
                return False, "same_transit_stack", None
        house = _house(item)
        if isinstance(house, int) and house_counts[house] >= 2:
            return False, "same_house_overflow", None
        if _strength(item) < 0.03:
            return False, "low_strength", None
        if not eid:
            return False, "low_strength", None
        return True, "", None

    def _add(item: Dict[str, Any], reason: str) -> bool:
        ok, why, dupe_of = _can_add(item)
        if not ok:
            skipped.append({"event_id": _event_id(item), "reason": why, "dupe_of": dupe_of})
            return False
        eid = _event_id(item)
        selected.append(item)
        reasons.setdefault(eid, []).append(reason)
        sig = _signature_key(item)
        signature_seen[sig] = eid
        cluster_seen[_cluster_key(item)] = eid
        body_counts[str(item.get("transit_body") or "").lower()] += 1
        house = _house(item)
        if isinstance(house, int):
            house_counts[house] += 1
        covered_domains.add(_domain(item))
        salience_map[eid] = _salience(item)
        return True
    def _pick_best(pool: Sequence[Mapping[str, Any]]) -> Mapping[str, Any] | None:
        candidates = [item for item in pool if _event_id(item)]
        if not candidates:
            return None
        return sorted(
            candidates,
            key=lambda item: (-_salience(item), -_strength(item), str(item.get("event_id") or "")),
        )[0]

    selected_ids = {str(s.get("event_id") or "") for s in selected}

    # Coverage anchors:
    # 1) angles (ASC/DSC prioritized)
    angle_pool = [
        item
        for item in typed
        if str(item.get("scope") or "") == "transit_to_angles"
        and str(item.get("bucket") or "").lower() in {"long", "medium"}
    ]
    angle_pool = sorted(
        angle_pool,
        key=lambda item: (
            -_salience(item),
            ANGLE_PRIORITY.get(str(item.get("natal_point") or "").upper(), 9),
            str(item.get("event_id") or ""),
        ),
    )
    for candidate in angle_pool:
        if len(selected) >= max_cards:
            break
        if _add(dict(candidate), "coverage:angles"):
            selected_ids.add(_event_id(candidate))
            break

    # 2) mind axis (3/9)
    mind_pool = [
        item
        for item in typed
        if _event_id(item) not in selected_ids
        and (_house(item) in {3, 9} or _target_house(item) in {3, 9})
    ]
    best_mind = _pick_best(mind_pool)
    if best_mind is not None and len(selected) < max_cards:
        if _add(dict(best_mind), "coverage:mind_3_9"):
            selected_ids.add(_event_id(best_mind))

    # 3) transform axis (Uranus/Pluto)
    transform_pool = [
        item
        for item in typed
        if _event_id(item) not in selected_ids and str(item.get("transit_body") or "").lower() in OUTER_STACK
    ]
    best_transform = _pick_best(transform_pool)
    if best_transform is not None and len(selected) < max_cards:
        if _add(dict(best_transform), "coverage:uranus_pluto"):
            selected_ids.add(_event_id(best_transform))

    # Fill with salience + domain diversity + cluster uniqueness
    def _fill_score(item: Mapping[str, Any]) -> float:
        score = _salience(item)
        domain = _domain(item)
        if domain not in covered_domains:
            score += 0.06
        body = str(item.get("transit_body") or "").lower()
        if body_counts[body] == 0:
            score += 0.03
        if str(item.get("bucket") or "").lower() == "long":
            score += 0.03
        if str(item.get("polarity") or "").lower() == "soft":
            score += 0.02
        return score

    remaining = [item for item in typed if _event_id(item) not in selected_ids]
    remaining.sort(key=lambda item: (-_fill_score(item), str(item.get("event_id") or "")))
    for item in remaining:
        if len(selected) >= max_cards:
            break
        domain = _domain(item)
        if _add(dict(item), f"fill:{domain}"):
            selected_ids.add(_event_id(item))

    meta = {
        "selection_mode": "coverage_first_v1",
        "selected_ids": [str(item.get("event_id") or "") for item in selected],
        "reasons": reasons,
        "salience": salience_map,
        "cluster_keys": {str(item.get("event_id") or ""): _cluster_key(item) for item in selected},
        "skipped_due_to_dedup": skipped,
    }
    return selected[:max_cards], meta


def _is_public_allowed(item: Mapping[str, Any]) -> bool:
    return is_public_event(item)
