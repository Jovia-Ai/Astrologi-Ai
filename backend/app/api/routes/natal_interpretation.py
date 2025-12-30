"""API route for natal chart interpretation using the rule engine."""
from __future__ import annotations

import copy
import logging
from types import SimpleNamespace
from typing import Any, Dict, List, Mapping, Sequence


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.ai.narrative.formatter import (
    build_formatted_aspects,
    build_formatted_house_positions,
    build_formatted_planet_positions,
)
from app.builders.composite_fragments import CompositeFragmentsBuilder
from app.builders.composite_guidance import build_guidance
from app.builders.composite_interpreter import CompositeInterpretationBuilder
from app.builders.composite_regulator import build_composite_regulation
from app.builders.narrative_builder import JoviaSemanticNarrativeBuilder, SLOT_NAMES
from app.builders.phase2_selector import select_phase2_fragments
from app.builders.semantic_normalizer import contains_verb_phrase, normalize_slot_text
from app.engine.aspect_mechanics import AspectMechanicsEngine
from app.engine.composite_engine import CompositeEngine
from app.engine.pattern_engine import PatternEmphasisEngine
from app.engine.router import build_combined_insights
from app.engine.rule_engine import CATEGORIES, RuleEngine, TYPE_NAMES
from app.engine.upper_meaning_engine import UpperMeaningEngine
from app.engine.meaning_weighting import build_meaning_weighting
from app.engine.narrative_anchor import build_narrative_anchor
from app.engine.inquiry_engine import InquiryEngine
from app.engine.dispositor_flow import DispositorFlowEngine
from app.engine.activation_sensitivity import ActivationSensitivityEngine
from app.engine.axis_activation import AxisActivationEngine
from app.engine.latent_potential import LatentPotentialEngine
from app.helpers.pressure_support import calculate_pressure_support
from app.helpers.strain_resilience import build_strain_resilience
from app.resolvers.expression_resolver import ExpressionResolver
from app.services.chart_service import (
    compute_natal_chart,
    serialize_aspects,
    serialize_planets,
)
from app.helpers.narrative_context import derive_core_aspects, derive_placements
from app.helpers.domain_normalizer import canon_domain

logger = logging.getLogger(__name__)

router = APIRouter(tags=["natal"])
rule_engine = RuleEngine()


class NatalInterpretationRequest(BaseModel):
    """Request body containing the birth data required for natal calculations."""

    birth_date: str = Field(..., description="Birth date in YYYY-MM-DD format.")
    birth_time: str = Field(..., description="Birth time in HH:MM format.")
    birth_place: str = Field(..., description="City + country or recognizable location label.")

    class Config:
        anystr_strip_whitespace = True


@router.post("/interpret")
def interpret_natal_chart(request: NatalInterpretationRequest, debug: bool = False) -> Dict[str, Any]:
    """Free deterministic interpretation endpoint (JoviaWeighted narratives)."""

    base_payload = _prepare_payload(request, premium_mode=False, debug_mode=debug)
    return _finalize_response(base_payload, premium_mode=False, debug_mode=debug)


@router.post("/interpret/premium")
def interpret_natal_chart_premium(request: NatalInterpretationRequest, debug: bool = False) -> Dict[str, Any]:
    """Premium endpoint (PRO Jovia narratives)."""

    base_payload = _prepare_payload(request, premium_mode=True, debug_mode=debug)
    return _finalize_response(base_payload, premium_mode=True, debug_mode=debug)


def _build_metadata(request: NatalInterpretationRequest, chart_data: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "birth_date": request.birth_date,
        "birth_time": request.birth_time,
        "birth_place": request.birth_place,
        "location": chart_data.get("location"),
        "birth_datetime": chart_data.get("birth_datetime"),
        "timezone": chart_data.get("timezone"),
    }


def _prepare_payload(
    request: NatalInterpretationRequest,
    *,
    premium_mode: bool,
    debug_mode: bool = False,
) -> Dict[str, Any]:
    try:
        chart_data = compute_natal_chart(request.birth_date, request.birth_time, request.birth_place)
    except Exception as exc:  # pragma: no cover - network/env specific
        logger.exception("Failed to calculate natal chart from inputs")
        raise HTTPException(status_code=500, detail=f"Chart calculation failed: {exc}") from exc

    snapshots: Dict[str, Any] | None = {} if debug_mode else None

    planets = serialize_planets(chart_data.get("planets", {}))
    aspects = serialize_aspects(chart_data.get("aspects", []))
    interpretation, meta_info = rule_engine.interpret(planets=planets, aspects=aspects, return_meta=True)
    if snapshots is not None:
        snapshots["rule_engine_output_summary"] = _summarize_rule_engine(interpretation, meta_info)

    placements = derive_placements(planets)
    core_aspects = derive_core_aspects(aspects)
    composite_engine = CompositeEngine()
    composites = composite_engine.build_composites(chart_data)
    dispositor_engine = DispositorFlowEngine()
    dispositor_flow = dispositor_engine.build(placements)
    axis_engine = AxisActivationEngine()
    axis_activation = axis_engine.build(placements, core_aspects=aspects)
    aspect_engine = AspectMechanicsEngine()
    aspect_mechanics = aspect_engine.build(aspects)
    sensitivity_engine = ActivationSensitivityEngine()
    activation_sensitivity = sensitivity_engine.build(composites, aspect_mechanics)
    pattern_engine = PatternEmphasisEngine()
    patterns = pattern_engine.build(
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
    )
    latent_engine = LatentPotentialEngine()
    latent_potential = latent_engine.build(composites, patterns, aspect_mechanics)
    upper_engine = UpperMeaningEngine()
    upper_meanings = upper_engine.build(
        composites,
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
    guidance_probe: Dict[str, Any] = {
        "active_domains": list(composite_guidance.get("active_domains") or []),
    }
    if composite_guidance.get("domain_priority"):
        guidance_probe["domain_priority"] = composite_guidance.get("domain_priority")
    if snapshots is not None:
        snapshots["composite_guidance"] = _snapshot_composite_guidance(composite_guidance)

    narrative: Dict[str, str] = {}
    used_composites: List[str] = []
    narrative_meta: Dict[str, Any] = {}
    inquiry_engine = InquiryEngine()
    focus_result = inquiry_engine.select_focus(composites, patterns)
    domain_builder = CompositeInterpretationBuilder(
        composites,
        patterns,
        focus_composites=focus_result.get("focus_composites", []),
    )
    composite_interpretation = domain_builder.build()
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
    narrative_fragments, phase2_snapshot = _build_phase2_fragment_payload(phase2_fragments)
    narrative_anchor = build_narrative_anchor(
        fragments_by_domain=narrative_fragments,
        dominant_domain=meaning_weighting["dominant_domain"],
        meaning_weighting=meaning_weighting,
    )
    if snapshots is not None:
        snapshots["semantic_normalizer_output_summary"] = phase2_snapshot["summary"]
        snapshots["phase2_slots"] = phase2_snapshot["slots"]
    phase2_fragment_probe: Dict[str, Any] = {
        "domains": list(phase2_fragments.keys()),
        "slot_counts": {},
    }
    total_slots = len(SLOT_NAMES)
    for domain, entry in phase2_fragments.items():
        slots = entry.get("slots") or {}
        filled = sum(1 for slot_name in SLOT_NAMES if slots.get(slot_name))
        ratio = filled / total_slots if total_slots else 0.0
        phase2_fragment_probe["slot_counts"][domain] = ratio
    expression_profile_probe: Dict[str, Any] = {
        "tone": expression_profile.get("tone"),
        "sentence_length": expression_profile.get("sentence_length"),
        "fallback_mode": expression_profile.get("fallback_mode"),
    }
    builder = JoviaSemanticNarrativeBuilder(
        SimpleNamespace(
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
        )
    )
    narrative = builder.build()
    if builder.fallback_used:
        narrative_meta["fallback_used"] = True
    narrative_meta["expression_profile"] = expression_profile
    used_composites = list(builder.used_composite_ids)
    if snapshots is not None:
        snapshots["narrative_plan"] = builder.narrative_plan
    combined_insights = build_combined_insights(meta_info, interpretation)

    warnings = _collect_debug_warnings(
        phase2_snapshot,
        composite_guidance,
        builder,
        debug_mode,
    )

    runtime_info = {
        "engine": rule_engine.__class__.__name__,
        "narrative_builder": builder.__class__.__name__,
        "pipeline_version": "v2.4",
    }
    routing_info = {
        "active_domains_source": builder.narrative_debug_active_domains_source,
    }

    debug_info = {
        "used_domain_composites": domain_builder.used_composite_ids,
        "used_narrative_composites": used_composites,
        "triggered_patterns": sorted(patterns.keys()),
        "triggered_upper_meaning": [
            entry.get("composite_id")
            for entry in upper_meanings
            if entry.get("composite_id")
        ],
        "stellium_composites": sorted(
            comp_id for comp_id, meta in patterns.items() if meta.get("stellium")
        ),
        "dispositor_flow": dispositor_flow,
        "axis_activation": axis_activation,
        "activation_sensitivity": activation_sensitivity,
        "latent_potential": latent_potential,
        "composite_guidance": composite_guidance,
        "quality_actions_applied": builder.quality_actions_applied,
        "pressure_support": pressure_support,
        "meaning_weighting": meaning_weighting,
        "expression_profile": expression_profile,
        "narrative_anchor": narrative_anchor,
        "guidance_probe": guidance_probe,
        "expression_profile_probe": expression_profile_probe,
        "phase2_fragments_probe": phase2_fragment_probe,
        "runtime": runtime_info,
        "narrative_debug_selected_domains": builder.narrative_debug_selected_domains,
        "narrative_debug_selected_slots": builder.narrative_debug_selected_slots,
        "narrative_debug_source_fragment_ids": builder.narrative_debug_source_fragment_ids,
        "narrative_debug_active_domains_source": builder.narrative_debug_active_domains_source,
        "routing": routing_info,
    }
    if debug_mode:
        debug_info["warnings"] = warnings
        if snapshots:
            debug_info["snapshots"] = snapshots
    return {
        "metadata": _build_metadata(request, chart_data),
        "planets": planets,
        "aspects": aspects,
        "formatted_positions": build_formatted_planet_positions(chart_data),
        "formatted_houses": build_formatted_house_positions(chart_data),
        "formatted_aspects": build_formatted_aspects(chart_data),
        "interpretation": interpretation,
        "meta_info": meta_info,
        "combined_insights": combined_insights,
        "composites": composites,
        "patterns": patterns,
        "upper_meaning": upper_meanings,
        "aspect_mechanics": aspect_mechanics,
        "composite_interpretation": composite_interpretation,
        "dispositor_flow": dispositor_flow,
        "axis_activation": axis_activation,
        "activation_sensitivity": activation_sensitivity,
        "latent_potential": latent_potential,
        "composite_guidance": composite_guidance,
        "meaning_weighting": meaning_weighting,
        "narrative_anchor": narrative_anchor,
        "debug": debug_info,
        "__narrative_fragments": narrative_fragments,
        "_phase2_snapshot": phase2_snapshot,
        "narrative_interpretation": narrative,
        "narrative_meta": narrative_meta,
        "expression_profile": expression_profile,
    }
def _finalize_response(base_payload: Mapping[str, Any], *, premium_mode: bool, debug_mode: bool = False) -> Dict[str, Any]:
    response = {
        "metadata": base_payload["metadata"],
        "planets": base_payload["planets"],
        "aspects": base_payload["aspects"],
        "interpretation": base_payload["interpretation"],
        "meta_info": base_payload["meta_info"],
        "formatted_positions": base_payload["formatted_positions"],
        "formatted_houses": base_payload["formatted_houses"],
        "formatted_aspects": base_payload["formatted_aspects"],
        "combined_insights": base_payload["combined_insights"],
        "composites": base_payload["composites"],
        "patterns": base_payload["patterns"],
        "upper_meaning": base_payload["upper_meaning"],
        "aspect_mechanics": base_payload["aspect_mechanics"],
        "composite_interpretation": base_payload.get("composite_interpretation", {}),
        "dispositor_flow": base_payload["dispositor_flow"],
        "axis_activation": base_payload["axis_activation"],
        "activation_sensitivity": base_payload["activation_sensitivity"],
        "latent_potential": base_payload["latent_potential"],
        "composite_guidance": base_payload["composite_guidance"],
        "meaning_weighting": base_payload["meaning_weighting"],
        "narrative_anchor": base_payload["narrative_anchor"],
        "debug": base_payload["debug"],
        "narrative_interpretation": base_payload["narrative_interpretation"],
        "narrative_text": base_payload.get("narrative_text") or base_payload.get("narrative_interpretation"),
        "premium_mode": premium_mode,
        "expression_profile": base_payload.get("expression_profile"),
    }
    _ensure_narrative_presence(base_payload, response)
    if debug_mode:
        _record_final_response_snapshot(response, base_payload.get("debug") or {})
    return response


def _ensure_narrative_presence(base_payload: Mapping[str, Any], response: Dict[str, Any]) -> None:
    if response.get("narrative_interpretation"):
        return
    phase2_snapshot = base_payload.get("_phase2_snapshot") or {}
    accepted_domains = {
        str(entry.get("domain")).strip().lower()
        for entry in phase2_snapshot.get("slots", {}).get("accepted", [])
        if isinstance(entry.get("domain"), str) and entry.get("domain").strip()
    }
    if not accepted_domains:
        return
    fragments = base_payload.get("__narrative_fragments") or {}
    fallback = _build_fragment_paragraphs(fragments, sorted(accepted_domains))
    if not fallback:
        return
    response["narrative_interpretation"] = fallback
    debug_entry = response.get("debug")
    if isinstance(debug_entry, dict):
        debug_entry["narrative_fallback_domains"] = sorted(fallback.keys())
    logger.warning(
        "Narrative builder cleared paragraphs for %s despite fragments being selected; injecting fallback text.",
        sorted(accepted_domains),
    )


def _record_final_response_snapshot(response: Dict[str, Any], debug_entry: Mapping[str, Any]) -> None:
    snapshots = debug_entry.get("snapshots")
    if not isinstance(snapshots, dict):
        return
    final_snapshot = copy.deepcopy(response)
    debug_payload = final_snapshot.get("debug")
    if isinstance(debug_payload, dict):
        debug_payload = dict(debug_payload)
        debug_payload.pop("snapshots", None)
        final_snapshot["debug"] = debug_payload
    snapshots["final_response_payload"] = final_snapshot


def _summarize_rule_engine(
    interpretation: Mapping[str, Mapping[str, Sequence[Any]]],
    meta_info: Mapping[str, Any],
) -> Dict[str, Any]:
    domain_summary: Dict[str, Dict[str, int]] = {}
    total_sentences = 0
    for domain, tile in interpretation.items():
        if not isinstance(tile, Mapping):
            continue
        counts: Dict[str, int] = {}
        for type_name in TYPE_NAMES:
            bucket = tile.get(type_name) or []
            counts[type_name] = len(bucket)
            total_sentences += len(bucket)
        domain_summary[domain] = {"counts": counts, "total": sum(counts.values())}
    meta_snapshot = {
        "planet_count": len(meta_info.get("planet_signs", {}) or {}),
        "stellium_planets": meta_info.get("stellium_planets") or [],
        "aspect_pairs": len(meta_info.get("aspect_pairs") or []),
    }
    return {
        "domain_summary": domain_summary,
        "total_sentences": total_sentences,
        "meta": meta_snapshot,
    }


def _snapshot_composite_guidance(guidance: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "active_domains": list(guidance.get("active_domains") or []),
        "domain_priority": guidance.get("domain_priority") or {},
        "tone_modifiers": guidance.get("tone_modifiers") or {},
    }


def _collect_debug_warnings(
    phase2_snapshot: Mapping[str, Any],
    guidance: Mapping[str, Any],
    builder: JoviaSemanticNarrativeBuilder,
    debug_mode: bool,
) -> List[str]:
    if not debug_mode:
        return []
    warnings: List[str] = []
    accepted_slots = phase2_snapshot.get("slots", {}).get("accepted", [])
    if not accepted_slots:
        warnings.append("Phase2 slot map normalized to zero entries.")
    accepted_domains = {
        canon_domain(entry.get("domain"))
        for entry in accepted_slots
        if isinstance(entry.get("domain"), str)
    }
    accepted_domains = {domain for domain in accepted_domains if domain}
    active_domains = {
        canon_domain(domain)
        for domain in guidance.get("active_domains") or []
        if isinstance(domain, str)
    }
    active_domains = {domain for domain in active_domains if domain}
    if active_domains and not accepted_domains.intersection(active_domains):
        warnings.append(
            "Composite guidance active domains do not align with any selected phase2 slot domains."
        )
    drop_clause_count = phase2_snapshot.get("quality_gates_applied", {}).get("drop_clause", 0)
    if drop_clause_count > 2:
        warnings.append(f"Quality gate drop_clause triggered {drop_clause_count} times.")
    for domain, plan in getattr(builder, "narrative_plan", {}).items():
        canonical_domain = canon_domain(domain)
        compiler_input = str(plan.get("compiler_input") or "").strip()
        final_text = str(plan.get("final_text") or "").strip()
        if compiler_input and not final_text:
            domain_label = canonical_domain or domain
            warnings.append(
                f"Domain '{domain_label}' had compiler input ({len(compiler_input)} chars) but produced empty paragraph text."
            )
    return warnings


def _build_fragment_paragraphs(
    fragments: Mapping[str, Dict[str, Any]],
    domains: Sequence[str],
) -> Dict[str, str]:
    paragraphs: Dict[str, str] = {}
    seen: set[str] = set()
    for domain in domains:
        canonical_domain = canon_domain(domain)
        if not canonical_domain or canonical_domain in seen:
            continue
        seen.add(canonical_domain)
        entry = fragments.get(canonical_domain)
        if not isinstance(entry, Mapping):
            continue
        paragraph = _paragraph_from_fragment_slots(entry.get("slots") or {})
        if paragraph:
            paragraphs[canonical_domain] = paragraph
    return paragraphs


def _paragraph_from_fragment_slots(slots: Mapping[str, Any]) -> str | None:
    sentences: List[str] = []
    for slot in SLOT_NAMES:
        fragment = slots.get(slot)
        if not isinstance(fragment, Mapping):
            continue
        text = fragment.get("text") or fragment.get("_semantic_text")
        normalized = _normalize_fragment_sentence(text)
        if not normalized:
            continue
        if normalized[-1] not in ".!?":
            normalized = f"{normalized}."
        sentences.append(normalized)
    if sentences:
        return " ".join(sentences)
    return None


def _normalize_fragment_sentence(text: Any) -> str:
    if text is None:
        return ""
    cleaned = " ".join(str(text).strip().split())
    return cleaned


def _build_phase2_fragment_payload(
    phase2_fragments: Mapping[str, Mapping[str, Any]]
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
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


def _apply_semantic_normalization(payload: Dict[str, Dict[str, Any]]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Any]]:
    normalized_payload: Dict[str, Dict[str, Any]] = {}
    accepted: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
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
                        "original_text": original_text,
                        "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
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
                        "original_text": original_text,
                        "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
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
                        "original_text": original_text,
                        "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
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
                    "original_text": original_text,
                    "fragment_id": fragment.get("fragment_ref") or fragment.get("id"),
                    "source_composite_ids": fragment.get("source_composite_ids") or [],
                }
            )
        anchor = entry.get("anchor")
        normalized_payload[canonical_domain] = {
            "slots": normalized_slots,
            "anchor": anchor if isinstance(anchor, Mapping) else normalized_slots.get("cause"),
        }
    domains_with_accepted = sorted(summary["domains_with_accepted"])
    summary["domains_with_accepted"] = domains_with_accepted
    trace = {
        "slots": {
            "accepted": accepted,
            "rejected": rejected,
        },
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
        if canonical_domain == "identity":
            normalized[canonical_domain] = entry
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
