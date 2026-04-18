"""Faz 1 audit regression snapshot suite.

Hand-crafted 6 scoring/selection senaryosu için `build_archetype_profile`
çıktısının audit-ilgili dar projeksiyonu snapshot olarak dondurulur.
Faz 1 refactor PR'ları (orb policy, shadow selection, tie-break,
confidence policy) bu snapshot'ları kasıtlı kıracak — diff insan tarafından
gözden geçirilip `REGENERATE_NATAL_AUDIT_SNAPSHOTS=1` ile kabul edilir.

Narrow projection — sadece karar motoru alanlarını tutar (narrative text
değil): primary archetype order, shadow, primary contradiction, confidence
bucket, subprofile softening, why_this_not_that anahtar kümeleri.

Senaryolar `_fixtures/natal_audit_scenarios.json`'daki chart fixture'larına
tematik olarak eşlenir; burada primitive/selector input'ları hand-crafted —
PR 1 scope'u saf scoring/selection davranışı. Upstream pipeline regression'ı
`test_natal_v8_baseline_snapshot.py` tarafından ayrıca korunuyor.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Mapping

import pytest

from app.natal.archetype_profile import build_archetype_profile


_SNAPSHOT_DIR = Path(__file__).parent / "_artifacts" / "natal_audit"


def _primitive_scores(overrides: Mapping[str, float] | None = None) -> Dict[str, Any]:
    base = {
        "self_definition": 0.82,
        "inner_structure": 0.80,
        "methodical_drive": 0.74,
        "public_refinement": 0.68,
        "visible_presence": 0.54,
        "originality_drive": 0.63,
        "big_picture_vision": 0.56,
        "meaningful_expansion": 0.51,
        "mental_structuring": 0.78,
        "systems_thinking": 0.70,
        "network_luck": 0.34,
        "intimacy_depth": 0.65,
        "transformative_bonding": 0.58,
        "emotional_threshold": 0.61,
        "recharge_through_home": 0.46,
        "family_self_reliance": 0.42,
        "backstage_creation": 0.31,
        "push_pull_drive": 0.37,
    }
    if overrides:
        base.update(overrides)
    return {
        "primitive_scores": [
            {"primitive_id": primitive_id, "score": score}
            for primitive_id, score in base.items()
        ]
    }


def _master_selector() -> Dict[str, Any]:
    return {
        "identity_spine": {
            "primary_identity_spine": {
                "source_primitives": ["self_definition", "inner_structure"],
                "confidence": 0.84,
            },
            "secondary_balancing_line": {
                "source_primitives": ["originality_drive", "big_picture_vision"],
                "confidence": 0.76,
            },
            "relational_line": {
                "source_primitives": ["intimacy_depth", "emotional_threshold"],
                "confidence": 0.67,
            },
            "work_visibility_line": {
                "source_primitives": ["public_refinement", "methodical_drive"],
                "confidence": 0.74,
            },
            "shadow_protection_line": {
                "source_primitives": ["emotional_threshold", "recharge_through_home"],
                "confidence": 0.63,
            },
        }
    }


def _contradictions(contradiction_id: str, score: float) -> Dict[str, Any]:
    return {"top_signatures": [{"id": contradiction_id, "score": score}]}


def _feature_graph(public_score: float, private_score: float) -> Dict[str, Any]:
    return {
        "public_private_split": {
            "public_score": public_score,
            "private_score": private_score,
        }
    }


_SCENARIOS: Dict[str, Dict[str, Any]] = {
    "simple": {
        "description": "Baseline path — strong identity + moderate test consistency",
        "primitive_overrides": None,
        "contradiction": ("structure_vs_originality", 0.72),
        "feature_graph": (0.69, 0.44),
        "test_scores": {
            "builder": 0.88,
            "visionary": 0.62,
            "depthkeeper": 0.49,
            "guardian": 0.38,
        },
        "family_scores": {
            "structure_preference": 0.91,
            "mental_precision": 0.82,
            "execution_style": 0.78,
            "novelty_vs_structure": 0.64,
        },
        "birth_time_confidence": "exact",
        "answer_consistency": 0.83,
    },
    "angular_heavy": {
        "description": "Public visibility emphasis — MC / 10th house weight proxy",
        "primitive_overrides": {
            "public_refinement": 0.88,
            "visible_presence": 0.86,
            "methodical_drive": 0.82,
        },
        "contradiction": ("visibility_vs_private_preparation", 0.74),
        "feature_graph": (0.86, 0.28),
        "test_scores": {"builder": 0.85, "visionary": 0.58},
        "family_scores": {
            "visibility_preference": 0.94,
            "expression_style": 0.88,
            "audience_energy": 0.82,
            "structure_preference": 0.71,
        },
        "birth_time_confidence": "exact",
        "answer_consistency": 0.81,
    },
    "stellium": {
        "description": "Capricorn 1st house stellium proxy — earth/structure dominance",
        "primitive_overrides": {
            "self_definition": 0.92,
            "inner_structure": 0.92,
            "methodical_drive": 0.88,
            "public_refinement": 0.78,
        },
        "contradiction": ("structure_vs_originality", 0.68),
        "feature_graph": (0.55, 0.52),
        "test_scores": {"builder": 0.93, "visionary": 0.41},
        "family_scores": {
            "structure_preference": 0.95,
            "responsibility_style": 0.89,
            "execution_style": 0.84,
            "mental_precision": 0.80,
        },
        "birth_time_confidence": "exact",
        "answer_consistency": 0.86,
    },
    "unknown_birthtime": {
        "description": "birth_time_confidence=unknown — chart_only weight profile, softened subprofile. Audit C3 revised: primary archetype IS selected (no runtime block).",
        "primitive_overrides": None,
        "contradiction": ("structure_vs_originality", 0.65),
        "feature_graph": (0.60, 0.48),
        "test_scores": None,
        "family_scores": {
            "structure_preference": 0.88,
            "mental_precision": 0.84,
        },
        "birth_time_confidence": "unknown",
        "answer_consistency": None,
    },
    "contradiction_heavy": {
        "description": "T-square proxy — high contradiction score + push/pull emphasis",
        "primitive_overrides": {
            "push_pull_drive": 0.82,
            "originality_drive": 0.78,
            "inner_structure": 0.74,
            "self_definition": 0.71,
        },
        "contradiction": ("composure_vs_internal_pressure", 0.86),
        "feature_graph": (0.58, 0.60),
        "test_scores": {"builder": 0.72, "visionary": 0.70, "depthkeeper": 0.58},
        "family_scores": {
            "stress_regulation": 0.88,
            "conflict_activation": 0.82,
            "novelty_vs_structure": 0.76,
            "change_tolerance": 0.71,
        },
        "birth_time_confidence": "exact",
        "answer_consistency": 0.74,
    },
    "saturn_heavy": {
        "description": "Saturn-dominant baseline — pre-dignity scoring. Faz 2 dignity integration will shift this.",
        "primitive_overrides": {
            "inner_structure": 0.94,
            "methodical_drive": 0.90,
            "self_definition": 0.78,
            "public_refinement": 0.72,
            "family_self_reliance": 0.58,
        },
        "contradiction": ("structure_vs_originality", 0.64),
        "feature_graph": (0.62, 0.50),
        "test_scores": {"builder": 0.91, "guardian": 0.64, "depthkeeper": 0.52},
        "family_scores": {
            "responsibility_style": 0.94,
            "structure_preference": 0.92,
            "safety_needs": 0.82,
            "execution_style": 0.86,
        },
        "birth_time_confidence": "exact",
        "answer_consistency": 0.82,
    },
}


def _confidence_band(value: float) -> str:
    if value < 0.55:
        return "low"
    if value < 0.75:
        return "mid"
    return "high"


def _narrow_projection(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Audit-relevant narrow projection — selection/scoring surface only.

    Excluded on purpose: narrative text fields (portrait_tr, plain_summary_tr,
    reasoning_tr, copy_blocks, mixins text, etc.) — those belong to Faz 3.
    """
    top = payload.get("top_archetypes") or []
    shadow = payload.get("shadow_archetype") or {}
    contradiction = payload.get("primary_contradiction") or {}
    confidence = payload.get("confidence") or {}

    primary_ids = [str(item.get("id") or "") for item in top]
    subprofile_ids = [
        {
            "archetype": str(item.get("id") or ""),
            "subprofile": str(item.get("subprofile_id") or ""),
            "is_softened": bool(item.get("subprofile_is_softened")),
        }
        for item in top
    ]
    why_keys: list[list[str]] = []
    for item in top:
        wtnt = item.get("why_this_not_that")
        if isinstance(wtnt, Mapping):
            why_keys.append(sorted(wtnt.keys()))
        elif isinstance(wtnt, list):
            why_keys.append(sorted(
                str(entry.get("runner_up") or "") for entry in wtnt
                if isinstance(entry, Mapping)
            ))
        else:
            why_keys.append([])

    slots = payload.get("slots") or {}

    primary_threshold_flags = [
        {
            "archetype": str(item.get("id") or ""),
            "meets_threshold": bool(item.get("score_meets_primary_threshold")),
        }
        for item in top
    ]
    aspect_direction_breakdowns = [
        {
            "archetype": str(item.get("id") or ""),
            "breakdown": item.get("aspect_direction_breakdown") or {},
        }
        for item in top
    ]

    return {
        "engine_version": payload.get("engine_version"),
        "taxonomy_version": payload.get("taxonomy_version"),
        "fusion_version": payload.get("fusion_version"),
        "scoring_profile_version": payload.get("scoring_profile_version"),
        "birth_time_mode": payload.get("birth_time_mode"),
        "lunar_phase": payload.get("lunar_phase"),
        "primary_archetype_ids": primary_ids,
        "primary_threshold_flags": primary_threshold_flags,
        "aspect_direction_breakdowns": aspect_direction_breakdowns,
        "shadow_archetype_id": str(shadow.get("id") or ""),
        "primary_contradiction_id": str(contradiction.get("id") or ""),
        "primary_contradiction_score": round(float(contradiction.get("score") or 0.0), 4),
        "subprofile_ids": subprofile_ids,
        "why_this_not_that_keys": why_keys,
        "confidence": {
            "global": round(float(confidence.get("global") or 0.0), 4),
            "chart": round(float(confidence.get("chart") or 0.0), 4),
            "test": round(float(confidence.get("test") or 0.0), 4),
        },
        "confidence_band": {
            "global": _confidence_band(float(confidence.get("global") or 0.0)),
            "chart": _confidence_band(float(confidence.get("chart") or 0.0)),
        },
        "slots": {
            str(slot_name): str(slot_value) if isinstance(slot_value, str) else slot_value
            for slot_name, slot_value in (slots.items() if isinstance(slots, Mapping) else [])
        },
        "chart_prior_profile": (payload.get("chart_prior") or {}).get("weight_profile"),
    }


def _run_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    payload = build_archetype_profile(
        primitive_scores=_primitive_scores(scenario.get("primitive_overrides")),
        master_selector=_master_selector(),
        contradiction_signatures=_contradictions(*scenario["contradiction"]),
        natal_feature_graph=_feature_graph(*scenario["feature_graph"]),
        test_scores=scenario.get("test_scores"),
        question_family_scores=scenario.get("family_scores") or {},
        birth_time_confidence=scenario.get("birth_time_confidence") or "exact",
        answer_consistency=scenario.get("answer_consistency"),
    )
    return _narrow_projection(payload)


def _snapshot_path(scenario_id: str) -> Path:
    return _SNAPSHOT_DIR / f"{scenario_id}.json"


def _serialize(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)


@pytest.mark.parametrize("scenario_id", sorted(_SCENARIOS.keys()))
def test_natal_audit_snapshot(scenario_id: str) -> None:
    projection = _run_scenario(_SCENARIOS[scenario_id])
    snapshot_path = _snapshot_path(scenario_id)
    regenerate = os.getenv("REGENERATE_NATAL_AUDIT_SNAPSHOTS") == "1"

    if not snapshot_path.exists() or regenerate:
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        snapshot_path.write_text(_serialize(projection), encoding="utf-8")
        if not regenerate:
            pytest.skip(
                f"audit snapshot generated: {snapshot_path.name} (re-run to enforce)"
            )
        return

    expected = json.loads(snapshot_path.read_text(encoding="utf-8"))
    if projection != expected:
        diffs = _diff_summary(expected, projection)
        pytest.fail(
            f"audit snapshot drifted for '{scenario_id}':\n{diffs}\n"
            f"Snapshot: {snapshot_path}\n"
            "Set REGENERATE_NATAL_AUDIT_SNAPSHOTS=1 to accept the new baseline."
        )


def _diff_summary(expected: Any, actual: Any, path: str = "$", max_items: int = 16) -> str:
    diffs: list[str] = []

    def _walk(exp: Any, act: Any, p: str) -> None:
        if len(diffs) >= max_items:
            return
        if type(exp) is not type(act):
            diffs.append(f"{p}: type {type(exp).__name__} -> {type(act).__name__}")
            return
        if isinstance(exp, dict):
            for key in sorted(set(exp.keys()) | set(act.keys())):
                if key not in exp:
                    diffs.append(f"{p}.{key}: ADDED ({act[key]!r})")
                elif key not in act:
                    diffs.append(f"{p}.{key}: REMOVED")
                else:
                    _walk(exp[key], act[key], f"{p}.{key}")
        elif isinstance(exp, list):
            if len(exp) != len(act):
                diffs.append(f"{p}: list len {len(exp)} -> {len(act)}")
            for idx, (a, b) in enumerate(zip(exp, act)):
                _walk(a, b, f"{p}[{idx}]")
        elif exp != act:
            diffs.append(f"{p}: {exp!r} -> {act!r}")

    _walk(expected, actual, path)
    if not diffs:
        return "(no symbolic diff)"
    return "\n".join(diffs)
