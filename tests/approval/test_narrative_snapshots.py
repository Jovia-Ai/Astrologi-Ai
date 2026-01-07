from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.builders.phase2_selector import select_phase2_fragments
from app.builders.semantic_normalizer import contains_verb_phrase, normalize_slot_text
from app.engine.activation_sensitivity import ActivationSensitivityEngine
from app.engine.aspect_mechanics import AspectMechanicsEngine
from app.engine.axis_activation import AxisActivationEngine
from app.engine.composite_engine import CompositeEngine
from app.engine.dispositor_flow import DispositorFlowEngine
from app.engine.inquiry_engine import InquiryEngine
from app.engine.latent_potential import LatentPotentialEngine
from app.engine.meaning_weighting import build_meaning_weighting
from app.engine.narrative_anchor import build_narrative_anchor
from app.engine.pattern_engine import PatternEmphasisEngine
from app.engine.rule_engine import RuleEngine
from app.engine.upper_meaning_engine import UpperMeaningEngine
from app.helpers.domain_normalizer import canon_domain
from app.helpers.narrative_context import derive_core_aspects, derive_placements
from app.helpers.pressure_support import calculate_pressure_support
from app.helpers.strain_resilience import build_strain_resilience
from app.resolvers.expression_resolver import ExpressionResolver
from app.builders.composite_guidance import build_guidance
from app.builders.composite_regulator import build_composite_regulation
from app.builders.narrative_builder import JoviaSemanticNarrativeBuilder, SLOT_NAMES
from app.builders.output_compactor import build_user_compact


FIXTURES = Path(__file__).resolve().parent / "fixtures" / "narrative_snapshots.json"
USER_FIXTURES = Path(__file__).resolve().parent / "fixtures" / "user_compact_snapshots.json"


def _build_payload(chart_data: Mapping[str, Any], *, tone_enabled: bool = True) -> Dict[str, Any]:
    planets = _serialize_planets(chart_data.get("planets", {}))
    aspects = _serialize_aspects(chart_data.get("aspects", []))
    rule_engine = RuleEngine()
    interpretation, meta_info = rule_engine.interpret(planets=planets, aspects=aspects, return_meta=True)

    placements = derive_placements(planets)
    core_aspects = derive_core_aspects(aspects)
    composite_engine = CompositeEngine()
    composites = composite_engine.build_composites(chart_data)
    dispositor_flow = DispositorFlowEngine().build(placements)
    axis_activation = AxisActivationEngine().build(placements, core_aspects=aspects)
    aspect_mechanics = AspectMechanicsEngine().build(aspects)
    activation_sensitivity = ActivationSensitivityEngine().build(composites, aspect_mechanics)
    patterns = PatternEmphasisEngine().build(
        composites,
        placements=placements,
        core_aspects=core_aspects,
        meta_info=meta_info,
    )
    regulations = build_composite_regulation(composites, patterns, axis_activation)
    domain_regulators = _primary_domain_regulations(composites, patterns, regulations)

    phase2_fragments = select_phase2_fragments(
        interpretation,
        composites,
        meta_info,
        domain_regulators,
        axis_activation,
    )
    latent_potential = LatentPotentialEngine().build(composites, patterns, aspect_mechanics)

    inquiry_engine = InquiryEngine()
    focus_result = inquiry_engine.select_focus(composites, patterns)
    upper_meanings = UpperMeaningEngine().build(
        focus_result.get("focus_composites", []),
        patterns,
        core_aspects=core_aspects,
        aspect_mechanics=aspect_mechanics,
    )

    composite_guidance = build_guidance(
        composites,
        patterns,
        meta_info,
        dispositor_flow,
        axis_activation,
        activation_sensitivity,
    )
    narrative_fragments, phase2_snapshot = _build_phase2_fragment_payload(phase2_fragments)
    pressure_support = calculate_pressure_support(composites, patterns, axis_activation)
    meaning_weighting = build_meaning_weighting(
        pressure_index=pressure_support["pressure_index"],
        support_index=pressure_support["support_index"],
        dominant_domain=pressure_support["dominant_domain"],
        theme_shares=None,
        patterns=patterns,
        theme_mapper_result=None,
    )
    meta_info["strain_resilience"] = build_strain_resilience(
        pressure_support=pressure_support,
        meaning_weighting=meaning_weighting,
        aspect_mechanics=aspect_mechanics,
    )
    expression_profile = ExpressionResolver.resolve(
        composite_output=composites,
        pressure_index=pressure_support["pressure_index"],
        support_index=pressure_support["support_index"],
        axis_balance=pressure_support["axis_balance"],
    )
    narrative_anchor = build_narrative_anchor(
        fragments_by_domain=narrative_fragments,
        dominant_domain=meaning_weighting["dominant_domain"],
        meaning_weighting=meaning_weighting,
    )

    builder = JoviaSemanticNarrativeBuilder(
        types.SimpleNamespace(
            composites=composites,
            patterns=patterns,
            upper_meanings=upper_meanings,
            meta_info=meta_info,
            aspect_mechanics=aspect_mechanics,
            dispositor_flow=dispositor_flow,
            axis_activation=axis_activation,
            activation_sensitivity=activation_sensitivity,
            fragments=narrative_fragments,
            narrative_anchor=narrative_anchor,
            guidance=composite_guidance,
            regulations=domain_regulators,
            expression_profile=expression_profile,
            quality_gates=phase2_snapshot["quality_gates_applied"],
            meaning_weighting=meaning_weighting,
            tone_enabled=tone_enabled,
        )
    )
    narrative = builder.build()
    return {
        "narrative_text": narrative,
        "phase2_snapshot": phase2_snapshot,
        "fragments": narrative_fragments,
        "latent_potential": latent_potential,
    }


def _build_phase2_fragment_payload(
    phase2_fragments: Mapping[str, Mapping[str, Any]]
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    payload: Dict[str, Dict[str, Any]] = {}
    for domain, entry in phase2_fragments.items():
        canonical_domain = canon_domain(domain)
        if not canonical_domain or canonical_domain in payload:
            continue
        if not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots")
        anchor = entry.get("anchor")
        if not isinstance(slots, Mapping):
            continue
        valid_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name in SLOT_NAMES:
            value = slots.get(slot_name)
            if isinstance(value, Mapping):
                valid_slots[slot_name] = dict(value)
        if not valid_slots:
            continue
        payload[canonical_domain] = {
            "slots": valid_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else valid_slots.get("cause"),
        }
    normalized_payload, normalization_trace = _apply_semantic_normalization(payload)
    normalized_payload = _normalize_phase2_texts(normalized_payload)
    return normalized_payload, normalization_trace


def _apply_semantic_normalization(
    payload: Dict[str, Dict[str, Any]]
) -> tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    normalized_payload: Dict[str, Dict[str, Any]] = {}
    accepted: list[Dict[str, Any]] = []
    rejected: list[Dict[str, Any]] = []
    summary = {
        "total_slots": 0,
        "accepted_slots": 0,
        "rejected_slots": 0,
        "rejection_reasons": {
            "no_text": 0,
            "empty_normalized": 0,
            "contains_verb_phrase": 0,
        },
        "domains_with_accepted": set(),
    }
    for domain, entry in payload.items():
        canonical_domain = canon_domain(domain)
        if not canonical_domain or not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots") or {}
        normalized_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            text = fragment.get("text")
            summary["total_slots"] += 1
            original_text = str(text).strip() if text else ""
            if not original_text:
                summary["rejection_reasons"]["no_text"] += 1
                summary["rejected_slots"] += 1
                rejected.append(
                    {
                        "domain": canonical_domain,
                        "slot": slot_name,
                        "reason": "no_text",
                    }
                )
                continue
            semantic_text = normalize_slot_text(text, slot_name)
            if not semantic_text:
                summary["rejection_reasons"]["empty_normalized"] += 1
                summary["rejected_slots"] += 1
                rejected.append(
                    {
                        "domain": canonical_domain,
                        "slot": slot_name,
                        "reason": "empty_after_normalize",
                    }
                )
                continue
            if contains_verb_phrase(semantic_text):
                summary["rejection_reasons"]["contains_verb_phrase"] += 1
                summary["rejected_slots"] += 1
                rejected.append(
                    {
                        "domain": canonical_domain,
                        "slot": slot_name,
                        "reason": "contains_verb_phrase",
                    }
                )
                continue
            normalized_fragment = dict(fragment)
            normalized_fragment["_semantic_text"] = semantic_text
            normalized_fragment["text"] = semantic_text
            normalized_slots[slot_name] = normalized_fragment
            summary["accepted_slots"] += 1
            summary["domains_with_accepted"].add(canonical_domain)
            accepted.append(
                {
                    "domain": canonical_domain,
                    "slot": slot_name,
                    "normalized_text": semantic_text,
                }
            )
        anchor = entry.get("anchor")
        normalized_payload[canonical_domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    summary["domains_with_accepted"] = sorted(summary["domains_with_accepted"])
    trace = {
        "slots": {"accepted": accepted, "rejected": rejected},
        "summary": summary,
        "quality_gates_applied": {"drop_clause": summary["rejected_slots"]},
    }
    return normalized_payload, trace


def _normalize_phase2_texts(payload: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    normalized: Dict[str, Dict[str, Any]] = {}
    for domain, entry in payload.items():
        canonical_domain = canon_domain(domain)
        if not canonical_domain or not isinstance(entry, Mapping):
            continue
        slots = entry.get("slots") or {}
        normalized_slots: Dict[str, Dict[str, Any]] = {}
        for slot_name, fragment in slots.items():
            if not isinstance(fragment, Mapping):
                continue
            text = fragment.get("text")
            normalized_text = normalize_slot_text(text, slot_name)
            normalized_fragment = dict(fragment)
            if normalized_text:
                normalized_fragment["text"] = normalized_text
            else:
                fallback = fragment.get("_semantic_text")
                if fallback:
                    normalized_fragment["text"] = fallback
            normalized_slots[slot_name] = normalized_fragment
        anchor = entry.get("anchor")
        normalized[canonical_domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    return normalized


def _primary_domain_regulations(
    composites: Sequence[Mapping[str, Any]],
    patterns: Mapping[str, Mapping[str, Any]],
    regulations: Mapping[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    primary: Dict[str, Dict[str, Any]] = {}
    for composite in sorted(
        composites,
        key=lambda comp: _extract_composite_priority(patterns, comp),
        reverse=True,
    ):
        domain = canon_domain(composite.get("domain"))
        comp_id = composite.get("composite_id")
        if not domain or not comp_id:
            continue
        if domain in primary:
            continue
        regulation = regulations.get(comp_id)
        if regulation:
            primary[domain] = regulation
    return primary


def _extract_composite_priority(
    patterns: Mapping[str, Mapping[str, Any]],
    composite: Mapping[str, Any],
) -> float:
    comp_id = composite.get("composite_id")
    meta = patterns.get(comp_id or "", {})
    try:
        return float(meta.get("priority_score") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _serialize_planets(planets_data: Mapping[str, Any]) -> list[Dict[str, Any]]:
    serialized: list[Dict[str, Any]] = []
    if not isinstance(planets_data, Mapping):
        return serialized
    for name, payload in planets_data.items():
        if not isinstance(payload, Mapping):
            continue
        serialized.append(
            {
                "planet": str(name),
                "sign": payload.get("sign"),
                "house": payload.get("house"),
                "degree": payload.get("longitude"),
            }
        )
    return serialized


def _serialize_aspects(aspects_data: Any) -> list[Dict[str, Any]]:
    serialized: list[Dict[str, Any]] = []
    if not isinstance(aspects_data, list):
        return serialized
    for aspect in aspects_data:
        if not isinstance(aspect, Mapping):
            continue
        planet_one = aspect.get("planet1")
        planet_two = aspect.get("planet2")
        aspect_type = aspect.get("type") or aspect.get("aspect")
        if not (planet_one and planet_two and aspect_type):
            continue
        orb_value = aspect.get("orb")
        if orb_value is None:
            expected = aspect.get("aspect_angle")
            exact = aspect.get("exact_angle") or aspect.get("angle")
            if isinstance(expected, (int, float)) and isinstance(exact, (int, float)):
                orb_value = abs(float(exact) - float(expected))
        serialized.append(
            {
                "planet1": str(planet_one),
                "planet2": str(planet_two),
                "type": str(aspect_type),
                "angle": aspect.get("angle"),
                "aspect_angle": aspect.get("aspect_angle"),
                "orb": orb_value,
                "exact_angle": aspect.get("exact_angle"),
            }
        )
    return serialized


def _load_snapshots() -> Dict[str, Any]:
    return json.loads(FIXTURES.read_text(encoding="utf-8"))


def _load_user_snapshots() -> Dict[str, Any]:
    return json.loads(USER_FIXTURES.read_text(encoding="utf-8"))


def _chart_samples() -> Dict[str, Dict[str, Any]]:
    return {
        "taurus_cancer": {
            "planets": {
                "sun": {"sign": "Taurus", "house": 1, "longitude": 30.0},
                "moon": {"sign": "Cancer", "house": 4, "longitude": 95.0},
                "mercury": {"sign": "Gemini", "house": 2, "longitude": 62.0},
            },
            "aspects": [],
            "location": {"name": "Fixture"},
        },
        "gemini_scorpio": {
            "planets": {
                "sun": {"sign": "Gemini", "house": 3, "longitude": 75.0},
                "moon": {"sign": "Scorpio", "house": 8, "longitude": 230.0},
                "venus": {"sign": "Libra", "house": 7, "longitude": 185.0},
            },
            "aspects": [],
            "location": {"name": "Fixture"},
        },
        "capricorn_aries": {
            "planets": {
                "sun": {"sign": "Capricorn", "house": 10, "longitude": 280.0},
                "moon": {"sign": "Aries", "house": 1, "longitude": 10.0},
                "mars": {"sign": "Aries", "house": 1, "longitude": 15.0},
            },
            "aspects": [],
            "location": {"name": "Fixture"},
        },
    }


def test_narrative_snapshots() -> None:
    snapshots = _load_snapshots()
    samples = _chart_samples()
    assert snapshots.keys() == samples.keys()
    for key, chart in samples.items():
        payload = _build_payload(chart)
        narrative = payload.get("narrative_text") or {}
        assert narrative == snapshots[key]


def test_user_compact_snapshots() -> None:
    snapshots = _load_user_snapshots()
    samples = _chart_samples()
    assert snapshots.keys() == samples.keys()
    for key, chart in samples.items():
        payload = _build_payload(chart)
        fragments = payload.get("fragments") or {}
        compact = build_user_compact(
            fragments,
            phase2_snapshot=payload.get("phase2_snapshot") or {},
        )
        assert compact == snapshots[key]
        domains = compact.get("domains") or []
        assert len(domains) <= 3
        for domain in domains:
            highlights = domain.get("highlights") or []
            assert len(highlights) <= 4
            for highlight in highlights:
                evidence = highlight.get("evidence") or []
                assert len(evidence) <= 2
        micro_insights = compact.get("micro_insights") or []
        assert len(micro_insights) <= 2
