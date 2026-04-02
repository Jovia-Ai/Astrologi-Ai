from __future__ import annotations

import os
from collections import Counter
from typing import Any, Dict, List, Mapping, Sequence, Tuple

from app.transit.narrative.chapter_role_engine import infer_chapter_role
from app.transit.narrative.event_feature_vector import build_event_feature_vector
from app.transit.narrative.hybrid_context import build_hybrid_event_context
from app.transit.narrative.natal_promise import build_natal_promise
from app.transit.narrative.personalization_context import extract_personalization_context
from app.transit.narrative.point_policy import is_public_event, point_weight
from app.transit.narrative.selection_evaluator import evaluate_period_selection

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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def select_event_ids(
    events: Sequence[Mapping[str, Any]],
    max_cards: int = 5,
    natal: Mapping[str, Any] | None = None,
    focus_date: str | None = None,
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
    natal_promise_cache: Dict[str, Dict[str, Any]] = {}
    feature_vector_cache: Dict[str, Dict[str, Any]] = {}
    chapter_role_cache: Dict[str, Dict[str, Any]] = {}
    story_score_map: Dict[str, float] = {}
    salience_map: Dict[str, float] = {}
    personalization_context = extract_personalization_context(natal)

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
            ranking = item.get("ranking") if isinstance(item.get("ranking"), Mapping) else {}
            try:
                weight = float(ranking.get("weight"))
            except (TypeError, ValueError):
                weight = 0.0
            if weight > 0:
                return min(1.0, max(0.05, weight / 1.6))
            tier = str(ranking.get("tier") or "").strip().lower()
            if tier == "main":
                return 0.78
            if tier == "support":
                return 0.58
            return 0.0

    def _orb(item: Mapping[str, Any]) -> float:
        try:
            return float(item.get("orb_deg"))
        except (TypeError, ValueError):
            return 9.9

    def _hybrid(item: Mapping[str, Any]) -> Dict[str, Any]:
        eid = _event_id(item)
        if eid not in hybrid_cache:
            hybrid_cache[eid] = build_hybrid_event_context(item, natal or {}, natal_promise=_natal_promise(item))
        return hybrid_cache[eid]

    def _natal_promise(item: Mapping[str, Any]) -> Dict[str, Any]:
        eid = _event_id(item)
        if eid not in natal_promise_cache:
            natal_promise_cache[eid] = build_natal_promise(item, natal or {})
        return natal_promise_cache[eid]

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

    def _focus_date_for_item(item: Mapping[str, Any]) -> str:
        if focus_date:
            return str(focus_date)
        timing = item.get("timing") if isinstance(item.get("timing"), Mapping) else {}
        for key in ("peak_date_utc", "entry_date_utc", "exit_date_utc"):
            raw = str(timing.get(key) or "").strip()
            if raw:
                return raw[:10]
        return "2000-01-01"

    def _feature_vector(item: Mapping[str, Any]) -> Dict[str, Any]:
        eid = _event_id(item)
        if eid not in feature_vector_cache:
            feature_vector_cache[eid] = build_event_feature_vector(
                item,
                selected_date=_focus_date_for_item(item),
                card=None,
                selected_day_context={},
                event_v2_meta=item,
                preview={},
                personalization_context=personalization_context,
                config=None,
            )
        return feature_vector_cache[eid]

    def _personalization_bonus(item: Mapping[str, Any]) -> float:
        personalization = _feature_vector(item).get("personalization") if isinstance(_feature_vector(item).get("personalization"), Mapping) else {}
        return round(
            (0.03 * _safe_float(personalization.get("natal_hot_house_match"), 0.0))
            + (0.025 * _safe_float(personalization.get("dominant_theme_match"), 0.0))
            + (0.02 * _safe_float(personalization.get("lens_match"), 0.0))
            + (0.015 * _safe_float(personalization.get("behavioral_history_match"), 0.0)),
            4,
        )

    def _chapter_role(item: Mapping[str, Any]) -> Dict[str, Any]:
        eid = _event_id(item)
        if eid not in chapter_role_cache:
            chapter_role_cache[eid] = infer_chapter_role(
                item,
                features=_feature_vector(item),
            )
        return chapter_role_cache[eid]

    def _period_story_score(item: Mapping[str, Any]) -> float:
        eid = _event_id(item)
        if eid in story_score_map:
            return story_score_map[eid]
        features = _feature_vector(item)
        meaning = features.get("meaning") if isinstance(features.get("meaning"), Mapping) else {}
        strength = features.get("strength") if isinstance(features.get("strength"), Mapping) else {}
        chapter = _chapter_role(item)
        score = (
            0.28 * _safe_float(meaning.get("structurality"), 0.0)
            + 0.18 * _safe_float(meaning.get("lasting_change"), 0.0)
            + 0.16 * _safe_float(strength.get("natal_resonance"), 0.0)
            + 0.14 * _safe_float(meaning.get("chapter_opening"), 0.0)
            + 0.10 * _safe_float(meaning.get("root_cause_weight"), 0.0)
            + 0.08 * _safe_float(strength.get("angle_activation"), 0.0)
            + 0.06 * (1.0 if str(item.get("bucket") or "").lower() == "long" else 0.55 if str(item.get("bucket") or "").lower() == "medium" else 0.18)
            + 0.06 * _safe_float((chapter.get("score") or 0.0), 0.0)
            + _personalization_bonus(item)
        )
        story_score_map[eid] = round(min(1.0, score), 4)
        return story_score_map[eid]

    def _story_mode_enabled() -> bool:
        raw = str(os.getenv("JOVIA_PERIOD_SELECTION_V2", "1")).strip().lower()
        return raw not in {"0", "false", "no", "off"}

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
        item["personalization_bonus"] = _personalization_bonus(item)
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

    def _pick_story_best(pool: Sequence[Mapping[str, Any]], *, prefer_new_domain: bool = False) -> Mapping[str, Any] | None:
        candidates = [item for item in pool if _event_id(item)]
        if not candidates:
            return None
        return sorted(
            candidates,
            key=lambda item: (
                -(
                    _period_story_score(item)
                    + (0.06 if prefer_new_domain and _domain(item) not in covered_domains else 0.0)
                    + (0.03 if str(_chapter_role(item).get("role") or "") not in {str(_chapter_role(sel).get("role") or "") for sel in selected} else 0.0)
                ),
                -_salience(item),
                str(item.get("event_id") or ""),
            ),
        )[0]

    def _has_angle_selected() -> bool:
        return any(str(item.get("scope") or "") == "transit_to_angles" for item in selected)

    def _has_mind_selected() -> bool:
        return any((_house(item) in {3, 9} or _target_house(item) in {3, 9}) for item in selected)

    def _has_transform_selected() -> bool:
        return any(str(item.get("transit_body") or "").lower() in OUTER_STACK for item in selected)

    def _support_role_order(spine_role: str) -> List[str]:
        mapping = {
            "builder": ["opener", "peak", "integrator", "release"],
            "opener": ["builder", "peak", "integrator", "release"],
            "peak": ["builder", "release", "integrator", "opener"],
            "release": ["builder", "integrator", "peak", "opener"],
            "integrator": ["builder", "opener", "peak", "release"],
        }
        return mapping.get(spine_role, ["builder", "opener", "peak", "integrator"])

    selected_ids = {str(s.get("event_id") or "") for s in selected}

    if _story_mode_enabled():
        story_pool = sorted(
            typed,
            key=lambda item: (-_period_story_score(item), -_salience(item), str(item.get("event_id") or "")),
        )
        spine = _pick_story_best(story_pool, prefer_new_domain=True)
        if spine is not None and len(selected) < max_cards:
            if _add(dict(spine), "story:spine"):
                selected_ids.add(_event_id(spine))

        if selected:
            spine_role = str(_chapter_role(selected[0]).get("role") or "builder")
            for role in _support_role_order(spine_role):
                if len(selected) >= min(max_cards, 3):
                    break
                role_pool = [
                    item
                    for item in typed
                    if _event_id(item) not in selected_ids and str(_chapter_role(item).get("role") or "") == role
                ]
                best_role = _pick_story_best(role_pool, prefer_new_domain=True)
                if best_role is not None and _add(dict(best_role), f"story:support:{role}"):
                    selected_ids.add(_event_id(best_role))

    # Coverage anchors:
    # 1) angles (ASC/DSC prioritized)
    if not _has_angle_selected():
        angle_pool = [
            item
            for item in typed
            if _event_id(item) not in selected_ids
            and str(item.get("scope") or "") == "transit_to_angles"
            and str(item.get("bucket") or "").lower() in {"long", "medium"}
        ]
        angle_pool = sorted(
            angle_pool,
            key=lambda item: (
                -max(_salience(item), _period_story_score(item)),
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
    if not _has_mind_selected():
        mind_pool = [
            item
            for item in typed
            if _event_id(item) not in selected_ids
            and (_house(item) in {3, 9} or _target_house(item) in {3, 9})
        ]
        best_mind = _pick_story_best(mind_pool, prefer_new_domain=True)
        if best_mind is not None and len(selected) < max_cards:
            if _add(dict(best_mind), "coverage:mind_3_9"):
                selected_ids.add(_event_id(best_mind))

    # 3) transform axis (Uranus/Pluto)
    if not _has_transform_selected():
        transform_pool = [
            item
            for item in typed
            if _event_id(item) not in selected_ids and str(item.get("transit_body") or "").lower() in OUTER_STACK
        ]
        best_transform = _pick_story_best(transform_pool, prefer_new_domain=True)
        if best_transform is not None and len(selected) < max_cards:
            if _add(dict(best_transform), "coverage:uranus_pluto"):
                selected_ids.add(_event_id(best_transform))

    # Fill with salience + domain diversity + cluster uniqueness
    def _fill_score(item: Mapping[str, Any]) -> float:
        score = _salience(item)
        story = _period_story_score(item)
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
        role = str(_chapter_role(item).get("role") or "")
        if role and role not in {str(_chapter_role(sel).get("role") or "") for sel in selected}:
            score += 0.04
        score += 0.08 * story
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
        "selection_mode": "story_first_v2" if _story_mode_enabled() else "coverage_first_v1",
        "selected_ids": [str(item.get("event_id") or "") for item in selected],
        "reasons": reasons,
        "salience": salience_map,
        "story_scores": {str(item.get("event_id") or ""): _period_story_score(item) for item in selected},
        "chapter_roles": {str(item.get("event_id") or ""): _chapter_role(item) for item in selected},
        "cluster_keys": {str(item.get("event_id") or ""): _cluster_key(item) for item in selected},
        "skipped_due_to_dedup": skipped,
        "evaluation": evaluate_period_selection(
            selected=selected,
            story_scores={str(item.get("event_id") or ""): _period_story_score(item) for item in selected},
            chapter_roles={str(item.get("event_id") or ""): _chapter_role(item) for item in selected},
        ),
    }
    return selected[:max_cards], meta


def _is_public_allowed(item: Mapping[str, Any]) -> bool:
    return is_public_event(item)
