from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Sequence

from app.transit.narrative.aspect_valence_mapper import (
    IntensityMode,
    ValenceMode,
    derive_valence_intensity,
)
from app.transit.narrative.manifestation_context_policy import build_manifestation_context


_BODY_NATURE = {
    "sun": "courage",
    "mars": "courage",
    "jupiter": "courage",
    "saturn": "responsibility",
    "moon": "regulation",
    "venus": "closeness",
    "pluto": "control",
    "neptune": "dissolution",
    "uranus": "change",
    "mercury": "clarity",
}

_DEFAULT_LINE_BY_DOMAIN = {
    "relationship": "relational_line",
    "career_visibility": "work_visibility_line",
    "growth_shadow": "shadow_protection_line",
    "emotional_security": "emotional_regulation_line",
    "identity": "primary_identity_line",
    "communication_learning": "growth_integration_line",
    "spiritual_meaning": "growth_integration_line",
}

_NATURE_PRIORITY = {
    "responsibility": 9,
    "control": 8,
    "dissolution": 7,
    "change": 6,
    "courage": 5,
    "closeness": 4,
    "regulation": 4,
    "intimacy": 4,
    "boundary": 3,
    "clarity": 2,
}

_AVOID_TAGS = [
    "generic_hat_copy",
    "coaching_command",
    "unbacked_natal_reason",
    "astro_first_opening",
]

_MEANING_INTENTS = {
    "responsibility_selection",
    "trust_calibration",
    "boundary_repair",
    "softening",
    "activation",
    "visibility_alignment",
    "reorientation",
    "release_invitation",
    "integration_invitation",
    "self_naming",
    "attention_redirect",
    "relational_repair",
    "expressive_clearing",
    "emotional_regulation",
}

_RHETORICAL_FRAMES = {
    "reframe",
    "sorting",
    "threshold",
    "calibration",
    "mirror",
    "release",
    "embodiment",
    "naked",
}


def build_period_voice_policy(
    *,
    canonical_period_spine: Mapping[str, Any] | None,
    matched_events: Sequence[Mapping[str, Any]] | None,
    chapter_role: str | None = None,
    canonical_backing_node_ids: Sequence[str] | None = None,
    recent_rhetorical_frames: Sequence[str] | None = None,
    recent_valence_modes: Sequence[str] | None = None,
    semantic_focus_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    spine = canonical_period_spine if isinstance(canonical_period_spine, Mapping) else {}
    if not spine:
        return {}

    spine_line = _select_spine_line(spine)
    if not spine_line:
        return {}

    events = [dict(item) for item in (matched_events or []) if isinstance(item, Mapping)]
    event_nature, event_nature_source = _select_event_nature(events, spine_line=spine_line)
    event_bodies = _event_bodies(events)
    backing_ids = _clean_strings(canonical_backing_node_ids) or _clean_strings([spine.get("target_node_id")])
    role = str(chapter_role or "").strip().lower() or _event_chapter_role(events) or "builder"
    manifestation_context = build_manifestation_context(
        matched_events=events,
        spine_line=spine_line,
        event_nature=event_nature,
        chapter_role=role,
    )
    semantic_focus = _semantic_focus_mapping(semantic_focus_result)
    semantic_focus_source = str(semantic_focus.get("source") or "").strip()
    semantic_focus_confidence = _safe_float(semantic_focus.get("confidence"), 0.0)
    semantic_focus_meaning_family = str(semantic_focus.get("meaning_family") or "").strip()
    semantic_focus_selected_meaning = str(semantic_focus.get("selected_meaning") or "").strip()
    meaning_intent = _select_meaning_intent(
        spine_line=spine_line,
        event_nature=event_nature,
        event_bodies=event_bodies,
        chapter_role=role,
        has_natal_backing=bool(backing_ids),
    )
    if semantic_focus_source and semantic_focus_source != "unknown" and semantic_focus_confidence >= 0.55:
        meaning_intent = semantic_focus_meaning_family or semantic_focus_selected_meaning or meaning_intent
    rhetorical_frame, frame_debug = _select_rhetorical_frame(
        spine_line=spine_line,
        event_nature=event_nature,
        meaning_intent=meaning_intent,
        event_bodies=event_bodies,
        chapter_role=role,
        recent_rhetorical_frames=recent_rhetorical_frames,
    )
    valence_mode, intensity_mode, valence_debug = _select_valence_intensity(
        events=events,
        chapter_role=role,
        event_nature=event_nature,
        has_natal_backing=bool(backing_ids),
        recent_valence_modes=recent_valence_modes,
    )

    seeds, policy_match = _seed_pack(spine_line, event_nature)
    if not seeds:
        return {
            "version": "period_voice_policy_v1",
            "reason_line_allowed": False,
            "reason_line_seed": "",
            "meaning_intent": meaning_intent,
            "rhetorical_frame": rhetorical_frame,
            "valence_mode": valence_mode.value if valence_mode else "",
            "intensity_mode": intensity_mode.value if intensity_mode else "",
            "valence_debug": dict(valence_debug),
            "upper_meaning_seed": "",
            "frame_seed": f"{meaning_intent}.{rhetorical_frame}" if meaning_intent and rhetorical_frame else "",
            "manifestation_context": manifestation_context,
            "technical_hint_strategy": "proof_or_debug_only",
            "avoid_tags": list(_AVOID_TAGS),
            "debug": {
                "spine_line": spine_line,
                "event_nature": event_nature,
                "event_nature_source": event_nature_source,
                "policy_match": dict(policy_match),
                "match_level": str(policy_match.get("level") or ""),
                "chapter_role": role,
                "canonical_backing_node_ids": backing_ids,
                "meaning_intent": meaning_intent,
                "rhetorical_frame": rhetorical_frame,
                "valence_mode": valence_mode.value if valence_mode else "",
                "intensity_mode": intensity_mode.value if intensity_mode else "",
                "valence_debug": dict(valence_debug),
                "manifestation_context": manifestation_context,
                "frame_debug": frame_debug,
                "event_bodies": event_bodies,
                "semantic_focus_source": semantic_focus_source,
                "semantic_focus_confidence": semantic_focus_confidence,
                "matched_event_ids": [
                    str(item.get("event_id") or "").strip()
                    for item in events
                    if str(item.get("event_id") or "").strip()
                ],
            },
        }

    return {
        "version": "period_voice_policy_v1",
        "mechanism_lens": f"{spine_line}.{event_nature}",
        "psychological_process": seeds["psychological_process"],
        "higher_meaning": seeds["higher_meaning"],
        "growth_edge": seeds["growth_edge"],
        "what_it_builds": seeds["what_it_builds"],
        "reason_line_allowed": bool(backing_ids),
        "reason_line_seed": seeds["reason_line_seed"] if backing_ids else "",
        "meaning_intent": meaning_intent,
        "rhetorical_frame": rhetorical_frame,
        "valence_mode": valence_mode.value if valence_mode else "",
        "intensity_mode": intensity_mode.value if intensity_mode else "",
        "valence_debug": dict(valence_debug),
        "upper_meaning_seed": seeds["higher_meaning"],
        "frame_seed": f"{meaning_intent}.{rhetorical_frame}",
        "manifestation_context": manifestation_context,
        "technical_hint_strategy": "proof_or_debug_only",
        "fun_shadow_line": seeds.get("fun_shadow_line", ""),
        "avoid_tags": list(_AVOID_TAGS),
        "debug": {
            "spine_line": spine_line,
            "event_nature": event_nature,
            "event_nature_source": event_nature_source,
            "policy_match": dict(policy_match),
            "match_level": str(policy_match.get("level") or ""),
            "chapter_role": role,
            "canonical_backing_node_ids": backing_ids,
            "meaning_intent": meaning_intent,
            "rhetorical_frame": rhetorical_frame,
            "valence_mode": valence_mode.value if valence_mode else "",
            "intensity_mode": intensity_mode.value if intensity_mode else "",
            "valence_debug": dict(valence_debug),
            "manifestation_context": manifestation_context,
            "frame_debug": frame_debug,
            "event_bodies": event_bodies,
            "semantic_focus_source": semantic_focus_source,
            "semantic_focus_confidence": semantic_focus_confidence,
            "matched_event_ids": [
                str(item.get("event_id") or "").strip()
                for item in events
                if str(item.get("event_id") or "").strip()
            ],
        },
    }


def _semantic_focus_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if value is not None and is_dataclass(value):
        try:
            return dict(asdict(value))
        except Exception:
            return {}
    return {}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _select_spine_line(spine: Mapping[str, Any]) -> str:
    spine_lines = _clean_strings(spine.get("spine_lines") or [])
    if spine_lines:
        return spine_lines[0]
    primary_domain = str(spine.get("primary_domain") or "").strip()
    return _DEFAULT_LINE_BY_DOMAIN.get(primary_domain, "")


def _select_event_nature(events: Sequence[Mapping[str, Any]], *, spine_line: str) -> tuple[str, str]:
    contextual = _contextual_event_nature(events, spine_line=spine_line)
    if contextual:
        return (contextual, "spine_line_context")

    scores: dict[str, int] = {}
    for event in events:
        body = str(event.get("transit_body") or event.get("body") or "").strip().lower()
        nature = _BODY_NATURE.get(body)
        if nature:
            scores[nature] = scores.get(nature, 0) + _NATURE_PRIORITY.get(nature, 1)

        aspect = str(event.get("aspect") or "").strip().lower()
        if aspect in {"square", "opposition"} and body in {"saturn", "venus", "moon"}:
            scores["boundary"] = scores.get("boundary", 0) + 4
        if aspect in {"conjunction", "square", "opposition"} and body == "pluto":
            scores["control"] = scores.get("control", 0) + 4

    if not scores:
        return ("clarity", "default")
    return (sorted(scores.items(), key=lambda item: (-item[1], item[0]))[0][0], "weighted_event_signal")


def _contextual_event_nature(events: Sequence[Mapping[str, Any]], *, spine_line: str) -> str:
    bodies = {
        str(event.get("transit_body") or event.get("body") or "").strip().lower()
        for event in events
        if str(event.get("transit_body") or event.get("body") or "").strip()
    }

    if spine_line == "relational_line":
        if bodies & {"saturn"}:
            return "boundary"
        if bodies & {"moon", "venus"}:
            return "closeness"

    if spine_line == "work_visibility_line":
        if bodies & {"pluto"}:
            return "control"
        if bodies & {"saturn"}:
            return "responsibility"
        if bodies & {"sun", "mars", "jupiter"}:
            return "courage"

    if spine_line == "shadow_protection_line":
        if bodies & {"pluto"}:
            return "control"
        if bodies & {"neptune"}:
            return "dissolution"

    if spine_line == "growth_integration_line":
        if bodies & {"uranus"}:
            return "change"
        if bodies & {"saturn"}:
            return "responsibility"

    if spine_line == "emotional_regulation_line":
        if bodies & {"moon"}:
            return "regulation"
        if bodies & {"neptune"}:
            return "dissolution"
        if bodies & {"saturn"}:
            return "responsibility"

    if spine_line == "primary_identity_line":
        if bodies & {"sun", "mars", "jupiter"}:
            return "courage"
        if bodies & {"saturn"}:
            return "responsibility"
        if bodies & {"pluto"}:
            return "control"

    return ""


def _event_chapter_role(events: Sequence[Mapping[str, Any]]) -> str:
    for event in events:
        chapter_role = event.get("chapter_role") if isinstance(event.get("chapter_role"), Mapping) else {}
        role = str(chapter_role.get("role") or "").strip().lower()
        if role:
            return role
    return ""


def _event_bodies(events: Sequence[Mapping[str, Any]]) -> list[str]:
    values: list[str] = []
    for event in events:
        body = str(event.get("transit_body") or event.get("body") or "").strip().lower()
        if body and body not in values:
            values.append(body)
    return values


def _select_meaning_intent(
    *,
    spine_line: str,
    event_nature: str,
    event_bodies: Sequence[str],
    chapter_role: str,
    has_natal_backing: bool,
) -> str:
    bodies = set(event_bodies)
    role = str(chapter_role or "").strip().lower()

    if spine_line == "relational_line" and "saturn" in bodies:
        return "trust_calibration" if has_natal_backing else "boundary_repair"
    if spine_line == "relational_line" and event_nature == "closeness":
        return "relational_repair"
    if spine_line == "work_visibility_line" and "saturn" in bodies:
        return "responsibility_selection"
    if spine_line == "work_visibility_line" and event_nature == "control":
        return "visibility_alignment"
    if spine_line == "shadow_protection_line" and "neptune" in bodies:
        return "softening" if role != "release" else "release_invitation"
    if spine_line == "shadow_protection_line":
        return "attention_redirect"
    if spine_line == "primary_identity_line" and "mars" in bodies:
        return "activation"
    if spine_line == "primary_identity_line":
        return "self_naming"
    if spine_line == "growth_integration_line" and event_nature == "change":
        return "reorientation"
    if spine_line == "growth_integration_line":
        return "integration_invitation"
    if spine_line == "emotional_regulation_line":
        return "emotional_regulation"
    if event_nature == "dissolution":
        return "softening"
    if event_nature == "responsibility":
        return "responsibility_selection"
    if event_nature == "courage":
        return "visibility_alignment"
    return "attention_redirect"


def _select_rhetorical_frame(
    *,
    spine_line: str,
    event_nature: str,
    meaning_intent: str,
    event_bodies: Sequence[str],
    chapter_role: str,
    recent_rhetorical_frames: Sequence[str] | None,
) -> tuple[str, dict[str, Any]]:
    candidates = _frame_candidates(
        spine_line=spine_line,
        event_nature=event_nature,
        meaning_intent=meaning_intent,
        event_bodies=event_bodies,
        chapter_role=chapter_role,
    )
    recent = _clean_strings(recent_rhetorical_frames or [])
    previous = recent[-1] if recent else ""
    chosen = candidates[0]
    rotation_applied = False
    if previous and previous == chosen:
        for candidate in candidates[1:]:
            if candidate != previous:
                chosen = candidate
                rotation_applied = True
                break
    return chosen, {
        "candidates": candidates,
        "recent_rhetorical_frames": recent,
        "rotation_applied": rotation_applied,
    }


def _frame_candidates(
    *,
    spine_line: str,
    event_nature: str,
    meaning_intent: str,
    event_bodies: Sequence[str],
    chapter_role: str,
) -> list[str]:
    bodies = set(event_bodies)
    role = str(chapter_role or "").strip().lower()

    if spine_line == "relational_line" and "saturn" in bodies:
        return ["calibration", "mirror"] if meaning_intent == "trust_calibration" else ["mirror", "calibration"]
    if spine_line == "work_visibility_line" and "saturn" in bodies:
        return ["sorting", "threshold"] if role != "peak" else ["threshold", "sorting"]
    if spine_line == "shadow_protection_line" and "neptune" in bodies:
        return ["reframe", "naked"] if role != "release" else ["release", "naked"]
    if spine_line == "primary_identity_line" and "mars" in bodies:
        return ["threshold", "embodiment"] if role != "integrator" else ["embodiment", "threshold"]
    if spine_line == "growth_integration_line" and "uranus" in bodies:
        return ["reframe", "calibration"]
    if meaning_intent == "emotional_regulation":
        return ["embodiment", "naked"]
    if meaning_intent == "release_invitation":
        return ["release", "naked"]
    if meaning_intent == "visibility_alignment":
        return ["threshold", "reframe"]
    if meaning_intent == "responsibility_selection":
        return ["sorting", "threshold"]
    if event_nature == "dissolution":
        return ["naked", "reframe"]
    if event_nature == "closeness":
        return ["mirror", "calibration"]
    return ["reframe", "sorting"]


def _select_valence_intensity(
    *,
    events: Sequence[Mapping[str, Any]],
    chapter_role: str,
    event_nature: str,
    has_natal_backing: bool,
    recent_valence_modes: Sequence[str] | None,
) -> tuple[ValenceMode, IntensityMode, dict[str, Any]]:
    recent = _clean_strings(recent_valence_modes or [])
    selected_event = next((event for event in events if isinstance(event, Mapping)), {})
    transit_body = str(selected_event.get("transit_body") or selected_event.get("body") or "").strip()
    natal_point = str(selected_event.get("natal_point") or "").strip()
    aspect_type = str(selected_event.get("aspect") or "").strip()
    valence_mode, intensity_mode, debug = derive_valence_intensity(
        transit_body=transit_body,
        natal_point=natal_point,
        aspect_type=aspect_type,
        chapter_role=chapter_role,
        natal_backing=has_natal_backing,
        event_nature=event_nature,
    )
    candidates = _valence_candidates(
        primary=valence_mode,
        intensity_mode=intensity_mode,
        event_nature=event_nature,
        chapter_role=chapter_role,
        has_natal_backing=has_natal_backing,
    )
    previous = recent[-1] if recent else ""
    chosen = valence_mode
    rotation_applied = False
    if previous and previous == chosen.value:
        for candidate in candidates[1:]:
            if candidate.value != previous:
                chosen = candidate
                rotation_applied = True
                break
    debug.update(
        {
            "recent_valence_modes": recent,
            "rotation_applied": rotation_applied,
            "candidates": [candidate.value for candidate in candidates],
            "selected_event_id": str(selected_event.get("event_id") or "").strip(),
        }
    )
    return chosen, intensity_mode, debug


def _valence_candidates(
    *,
    primary: ValenceMode,
    intensity_mode: IntensityMode,
    event_nature: str,
    chapter_role: str,
    has_natal_backing: bool,
) -> list[ValenceMode]:
    candidates: list[ValenceMode] = [primary]
    role = str(chapter_role or "").strip().lower()
    nature = str(event_nature or "").strip().lower()

    if primary == ValenceMode.TENSION and intensity_mode == IntensityMode.DENSE:
        candidates.extend([ValenceMode.INTEGRATION, ValenceMode.MATURATION])
    elif primary == ValenceMode.INTEGRATION and intensity_mode == IntensityMode.DENSE:
        candidates.extend([ValenceMode.MATURATION, ValenceMode.MOMENTUM])
    elif primary == ValenceMode.OPENING:
        candidates.extend([ValenceMode.RECOGNITION, ValenceMode.MOMENTUM])
    elif primary == ValenceMode.RECOGNITION:
        candidates.extend([ValenceMode.OPENING, ValenceMode.MATURATION])
    elif primary == ValenceMode.MOMENTUM:
        candidates.extend([ValenceMode.INTEGRATION, ValenceMode.RECOGNITION])
    elif primary == ValenceMode.RELEASE:
        candidates.extend([ValenceMode.INTEGRATION, ValenceMode.OPENING])
    else:
        candidates.extend([ValenceMode.INTEGRATION, ValenceMode.OPENING])

    if role == "release" and ValenceMode.RELEASE not in candidates:
        candidates.append(ValenceMode.RELEASE)
    if role == "peak" and nature in {"courage", "control"} and ValenceMode.RECOGNITION not in candidates:
        candidates.append(ValenceMode.RECOGNITION)
    if has_natal_backing and nature == "responsibility" and ValenceMode.MATURATION not in candidates:
        candidates.append(ValenceMode.MATURATION)

    ordered: list[ValenceMode] = []
    for candidate in candidates:
        if candidate not in ordered:
            ordered.append(candidate)
    return ordered


def _seed_pack(spine_line: str, event_nature: str) -> tuple[dict[str, str], dict[str, Any]]:
    fallback_order = [
        (spine_line, event_nature, "exact"),
        (spine_line, "default", "spine_line_generic"),
        ("*", event_nature, "event_nature_generic"),
    ]
    for candidate_spine, candidate_nature, level in fallback_order:
        key = (candidate_spine, candidate_nature)
        seeds = _SEED_MATRIX.get(key)
        if seeds:
            return (
                dict(seeds),
                {
                    "level": level,
                    "seed_key": f"{candidate_spine}.{candidate_nature}",
                    "fallback_order": ["exact", "spine_line_generic", "event_nature_generic", "legacy_untouched"],
                },
            )
    return (
        {},
        {
            "level": "legacy_untouched",
            "seed_key": "",
            "fallback_order": ["exact", "spine_line_generic", "event_nature_generic", "legacy_untouched"],
        },
    )


def _clean_strings(values: Any) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        values = [values]
    out: list[str] = []
    for value in values:
        token = str(value or "").strip()
        if token and token not in out:
            out.append(token)
    return out


_SEED_MATRIX: dict[tuple[str, str], dict[str, str]] = {
    ("work_visibility_line", "courage"): {
        "psychological_process": "work_visibility_courage_process",
        "higher_meaning": "work_visibility_courage_meaning",
        "growth_edge": "work_visibility_courage_edge",
        "what_it_builds": "work_visibility_courage_build",
        "reason_line_seed": "work_visibility_courage_reason",
        "fun_shadow_line": "work_visibility_courage_shadow",
    },
    ("work_visibility_line", "responsibility"): {
        "psychological_process": "work_visibility_responsibility_process",
        "higher_meaning": "work_visibility_responsibility_meaning",
        "growth_edge": "work_visibility_responsibility_edge",
        "what_it_builds": "work_visibility_responsibility_build",
        "reason_line_seed": "work_visibility_responsibility_reason",
        "fun_shadow_line": "work_visibility_responsibility_shadow",
    },
    ("work_visibility_line", "control"): {
        "psychological_process": "work_visibility_control_process",
        "higher_meaning": "work_visibility_control_meaning",
        "growth_edge": "work_visibility_control_edge",
        "what_it_builds": "work_visibility_control_build",
        "reason_line_seed": "work_visibility_control_reason",
        "fun_shadow_line": "work_visibility_control_shadow",
    },
    ("work_visibility_line", "default"): {
        "psychological_process": "work_visibility_default_process",
        "higher_meaning": "work_visibility_default_meaning",
        "growth_edge": "work_visibility_default_edge",
        "what_it_builds": "work_visibility_default_build",
        "reason_line_seed": "work_visibility_default_reason",
        "fun_shadow_line": "work_visibility_default_shadow",
    },
    ("relational_line", "intimacy"): {
        "psychological_process": "relational_intimacy_process",
        "higher_meaning": "relational_intimacy_meaning",
        "growth_edge": "relational_intimacy_edge",
        "what_it_builds": "relational_intimacy_build",
        "reason_line_seed": "relational_intimacy_reason",
        "fun_shadow_line": "relational_intimacy_shadow",
    },
    ("relational_line", "closeness"): {
        "psychological_process": "relational_closeness_process",
        "higher_meaning": "relational_closeness_meaning",
        "growth_edge": "relational_closeness_edge",
        "what_it_builds": "relational_closeness_build",
        "reason_line_seed": "relational_closeness_reason",
        "fun_shadow_line": "relational_closeness_shadow",
    },
    ("relational_line", "responsibility"): {
        "psychological_process": "relational_responsibility_process",
        "higher_meaning": "relational_responsibility_meaning",
        "growth_edge": "relational_responsibility_edge",
        "what_it_builds": "relational_responsibility_build",
        "reason_line_seed": "relational_responsibility_reason",
        "fun_shadow_line": "relational_responsibility_shadow",
    },
    ("relational_line", "boundary"): {
        "psychological_process": "relational_boundary_process",
        "higher_meaning": "relational_boundary_meaning",
        "growth_edge": "relational_boundary_edge",
        "what_it_builds": "relational_boundary_build",
        "reason_line_seed": "relational_boundary_reason",
        "fun_shadow_line": "relational_boundary_shadow",
    },
    ("relational_line", "default"): {
        "psychological_process": "relational_default_process",
        "higher_meaning": "relational_default_meaning",
        "growth_edge": "relational_default_edge",
        "what_it_builds": "relational_default_build",
        "reason_line_seed": "relational_default_reason",
        "fun_shadow_line": "relational_default_shadow",
    },
    ("shadow_protection_line", "control"): {
        "psychological_process": "shadow_protection_control_process",
        "higher_meaning": "shadow_protection_control_meaning",
        "growth_edge": "shadow_protection_control_edge",
        "what_it_builds": "shadow_protection_control_build",
        "reason_line_seed": "shadow_protection_control_reason",
        "fun_shadow_line": "shadow_protection_control_shadow",
    },
    ("shadow_protection_line", "dissolution"): {
        "psychological_process": "shadow_protection_dissolution_process",
        "higher_meaning": "shadow_protection_dissolution_meaning",
        "growth_edge": "shadow_protection_dissolution_edge",
        "what_it_builds": "shadow_protection_dissolution_build",
        "reason_line_seed": "shadow_protection_dissolution_reason",
        "fun_shadow_line": "shadow_protection_dissolution_shadow",
    },
    ("shadow_protection_line", "default"): {
        "psychological_process": "shadow_protection_default_process",
        "higher_meaning": "shadow_protection_default_meaning",
        "growth_edge": "shadow_protection_default_edge",
        "what_it_builds": "shadow_protection_default_build",
        "reason_line_seed": "shadow_protection_default_reason",
        "fun_shadow_line": "shadow_protection_default_shadow",
    },
    ("growth_integration_line", "change"): {
        "psychological_process": "growth_integration_change_process",
        "higher_meaning": "growth_integration_change_meaning",
        "growth_edge": "growth_integration_change_edge",
        "what_it_builds": "growth_integration_change_build",
        "reason_line_seed": "growth_integration_change_reason",
        "fun_shadow_line": "growth_integration_change_shadow",
    },
    ("growth_integration_line", "responsibility"): {
        "psychological_process": "growth_integration_responsibility_process",
        "higher_meaning": "growth_integration_responsibility_meaning",
        "growth_edge": "growth_integration_responsibility_edge",
        "what_it_builds": "growth_integration_responsibility_build",
        "reason_line_seed": "growth_integration_responsibility_reason",
        "fun_shadow_line": "growth_integration_responsibility_shadow",
    },
    ("growth_integration_line", "default"): {
        "psychological_process": "growth_integration_default_process",
        "higher_meaning": "growth_integration_default_meaning",
        "growth_edge": "growth_integration_default_edge",
        "what_it_builds": "growth_integration_default_build",
        "reason_line_seed": "growth_integration_default_reason",
        "fun_shadow_line": "growth_integration_default_shadow",
    },
    ("emotional_regulation_line", "regulation"): {
        "psychological_process": "emotional_regulation_regulation_process",
        "higher_meaning": "emotional_regulation_regulation_meaning",
        "growth_edge": "emotional_regulation_regulation_edge",
        "what_it_builds": "emotional_regulation_regulation_build",
        "reason_line_seed": "emotional_regulation_regulation_reason",
        "fun_shadow_line": "emotional_regulation_regulation_shadow",
    },
    ("emotional_regulation_line", "default"): {
        "psychological_process": "emotional_regulation_default_process",
        "higher_meaning": "emotional_regulation_default_meaning",
        "growth_edge": "emotional_regulation_default_edge",
        "what_it_builds": "emotional_regulation_default_build",
        "reason_line_seed": "emotional_regulation_default_reason",
        "fun_shadow_line": "emotional_regulation_default_shadow",
    },
    ("primary_identity_line", "courage"): {
        "psychological_process": "primary_identity_courage_process",
        "higher_meaning": "primary_identity_courage_meaning",
        "growth_edge": "primary_identity_courage_edge",
        "what_it_builds": "primary_identity_courage_build",
        "reason_line_seed": "primary_identity_courage_reason",
        "fun_shadow_line": "primary_identity_courage_shadow",
    },
    ("primary_identity_line", "default"): {
        "psychological_process": "primary_identity_default_process",
        "higher_meaning": "primary_identity_default_meaning",
        "growth_edge": "primary_identity_default_edge",
        "what_it_builds": "primary_identity_default_build",
        "reason_line_seed": "primary_identity_default_reason",
        "fun_shadow_line": "primary_identity_default_shadow",
    },
    ("*", "control"): {
        "psychological_process": "generic_control_process",
        "higher_meaning": "generic_control_meaning",
        "growth_edge": "generic_control_edge",
        "what_it_builds": "generic_control_build",
        "reason_line_seed": "generic_control_reason",
        "fun_shadow_line": "generic_control_shadow",
    },
    ("*", "dissolution"): {
        "psychological_process": "generic_dissolution_process",
        "higher_meaning": "generic_dissolution_meaning",
        "growth_edge": "generic_dissolution_edge",
        "what_it_builds": "generic_dissolution_build",
        "reason_line_seed": "generic_dissolution_reason",
        "fun_shadow_line": "generic_dissolution_shadow",
    },
    ("*", "change"): {
        "psychological_process": "generic_change_process",
        "higher_meaning": "generic_change_meaning",
        "growth_edge": "generic_change_edge",
        "what_it_builds": "generic_change_build",
        "reason_line_seed": "generic_change_reason",
        "fun_shadow_line": "generic_change_shadow",
    },
    ("*", "courage"): {
        "psychological_process": "generic_courage_process",
        "higher_meaning": "generic_courage_meaning",
        "growth_edge": "generic_courage_edge",
        "what_it_builds": "generic_courage_build",
        "reason_line_seed": "generic_courage_reason",
        "fun_shadow_line": "generic_courage_shadow",
    },
    ("*", "closeness"): {
        "psychological_process": "generic_closeness_process",
        "higher_meaning": "generic_closeness_meaning",
        "growth_edge": "generic_closeness_edge",
        "what_it_builds": "generic_closeness_build",
        "reason_line_seed": "generic_closeness_reason",
        "fun_shadow_line": "generic_closeness_shadow",
    },
    ("*", "regulation"): {
        "psychological_process": "generic_regulation_process",
        "higher_meaning": "generic_regulation_meaning",
        "growth_edge": "generic_regulation_edge",
        "what_it_builds": "generic_regulation_build",
        "reason_line_seed": "generic_regulation_reason",
        "fun_shadow_line": "generic_regulation_shadow",
    },
}
