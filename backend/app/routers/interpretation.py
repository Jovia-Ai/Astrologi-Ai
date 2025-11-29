"""Interpretation routes and handlers."""
from __future__ import annotations

import logging
from typing import Any, Dict, Mapping, Sequence

from flask import Blueprint, jsonify, request

from app.ai.archetypes.analyzer import (
    clean_text,
    enforce_style_or_rewrite,
    generate_full_archetype_report,
    integrate_life_expression,
    limit_sentences,
    map_confidence_label,
    pick_axis,
)
from app.ai.narrative.groq_client import (
    call_groq_ai,
    get_ai_interpretation,
    request_refined_interpretation,
)
from app.ai.narrative.interpreter import (
    build_category_card,
    build_interpretation_categories,
    build_life_card,
    build_shadow_card,
    fallback_life_story,
    first_sentences,
    normalize_ai_payload,
    strip_label_prefix,
)
from app.ai.prompts import AI_PROMPT
from app.astro.chart_engine.builder import calculate_chart_from_birth_details
from app.core.errors import AIError

interpretation_bp = Blueprint("interpretation", __name__)
logger = logging.getLogger(__name__)


@interpretation_bp.route("/interpretation", methods=["POST", "OPTIONS"])
@interpretation_bp.route("/api/interpretation", methods=["POST", "OPTIONS"])
def interpretation():
    if request.method == "OPTIONS":
        return "", 204

    payload = request.get_json(silent=True)
    if not isinstance(payload, Mapping):
        logger.warning("Interpretation endpoint received invalid JSON payload: %s", payload)
        return jsonify({"error": "Invalid JSON payload."}), 400

    chart_data = payload.get("chart_data")
    alt_strategy = payload.get("alt_strategy")

    if not isinstance(chart_data, Mapping):
        birth_date = payload.get("birth_date") or payload.get("date")
        birth_time = payload.get("birth_time") or payload.get("time")
        birth_place = payload.get("birth_place") or payload.get("city")
        if not all((birth_date, birth_time, birth_place)):
            logger.warning("Interpretation endpoint missing chart_data and birth inputs: %s", payload)
            return jsonify({
                "error": "chart_data must be provided as an object OR birth_date/time/place must be supplied.",
            }), 400
        try:
            chart_data = calculate_chart_from_birth_details(birth_date, birth_time, birth_place)
        except Exception as exc:  # pragma: no cover - network/location failures
            logger.exception("Failed to build chart from inputs")
            return jsonify({"error": f"Failed to calculate chart: {exc}"}), 500

    chart_dict = dict(chart_data)

    try:
        archetype = generate_full_archetype_report(chart_dict)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to extract archetype data")
        return jsonify({"error": "Failed to extract archetype data."}), 500

    life_narrative = archetype.get("life_narrative")
    if not life_narrative:
        life_layer = integrate_life_expression(chart_dict, archetype_data=archetype)
        archetype.update(life_layer)
        life_narrative = life_layer.get("life_narrative")

    alternate_narrative = None
    if isinstance(alt_strategy, str):
        alt_layer = integrate_life_expression(chart_dict, archetype_data=archetype, strategy=alt_strategy)
        alternate_narrative = alt_layer.get("life_narrative")
        if alternate_narrative:
            archetype.update(alt_layer)
            life_narrative = alternate_narrative

    legacy_life_block: Dict[str, Any] = dict(life_narrative or {})

    try:
        ai_result = request_refined_interpretation(archetype, chart_dict)
    except AIError as exc:
        logger.error("Groq interpretation error: %s", exc)
        ai_result = get_ai_interpretation(chart_dict)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unexpected interpretation failure")
        ai_result = get_ai_interpretation(chart_dict)

    ai_payload = normalize_ai_payload(ai_result)
    categories = build_interpretation_categories(archetype, ai_payload)

    cards: Dict[str, Any] = {}
    life_card = build_life_card(ai_payload, life_narrative, archetype)
    if life_card:
        cards["life"] = life_card

    career_reasons = []
    life_focus = archetype.get("life_focus")
    story_tone = archetype.get("story_tone")
    if isinstance(life_focus, str) and life_focus.strip():
        career_reasons.append(f"Odak: {life_focus.strip()}")
    if isinstance(story_tone, str) and story_tone.strip():
        career_reasons.append(f"Ton: {story_tone.strip()}")
    career_card = build_category_card(
        categories.get("career") if isinstance(categories, Mapping) else None,
        default_title="İş & Amaç",
        extra_reasons=career_reasons,
    )
    if career_card:
        cards["career"] = career_card

    spiritual_reasons = []
    dominant_axis = archetype.get("dominant_axis")
    if isinstance(dominant_axis, str) and dominant_axis.strip():
        spiritual_reasons.append(f"Öne çıkan eksen: {dominant_axis.strip()}")
    spiritual_card = build_category_card(
        categories.get("spiritual") if isinstance(categories, Mapping) else None,
        default_title="Ruhsal Akış",
        extra_reasons=spiritual_reasons,
    )
    if spiritual_card:
        cards["spiritual"] = spiritual_card

    love_card = build_category_card(
        categories.get("love") if isinstance(categories, Mapping) else None,
        default_title="Aşk & İlişkiler",
    )
    if love_card:
        cards["love"] = love_card

    shadow_card = build_shadow_card(
        categories.get("shadow") if isinstance(categories, Mapping) else None,
        archetype.get("behavior_patterns") if isinstance(archetype, Mapping) else None,
    )
    if shadow_card:
        cards["shadow"] = shadow_card

    response_body: Dict[str, Any] = {
        "status": "success",
        "themes": archetype.get("core_themes", []),
        "ai_interpretation": ai_payload,
        "tone": archetype.get("story_tone"),
        "categories": categories,
        "archetype": archetype,
    }

    if life_card:
        primary_text = life_card.get("narrative", {}).get("main") if isinstance(life_card.get("narrative"), Mapping) else ""
        life_text = limit_sentences(primary_text or legacy_life_block.get("text") or "", min_sentences=3, max_sentences=6)
        if life_text:
            legacy_life_block["text"] = life_text
        axis_candidate = clean_text(legacy_life_block.get("axis") or archetype.get("dominant_axis") or "")
        axis_scores = payload.get("axis_scores") if isinstance(payload.get("axis_scores"), Mapping) else {}
        dominant_axis = pick_axis(axis_scores, axis_candidate or "Yay–İkizler")
        legacy_life_block["axis"] = dominant_axis
        legacy_life_block["confidence_label"] = life_card.get("confidence_label") or map_confidence_label(legacy_life_block.get("confidence"))
        if "correlations" not in legacy_life_block and archetype.get("correlations"):
            legacy_life_block["correlations"] = archetype.get("correlations")
        legacy_life_block["card"] = life_card
    if cards:
        expanded_cards = dict(cards)
        if "life" in cards:
            expanded_cards.setdefault("essence", cards["life"])
        if "career" in cards:
            expanded_cards.setdefault("path", cards["career"])
        if "love" in cards:
            expanded_cards.setdefault("heart", cards["love"])
        if "spiritual" in cards:
            expanded_cards.setdefault("mind", cards["spiritual"])
        response_body["cards"] = expanded_cards

    correlations = legacy_life_block.get("correlations") or archetype.get("correlations") or {}
    if not isinstance(correlations, Mapping):
        correlations = {}
    focus_value = legacy_life_block.get("focus") or archetype.get("life_focus")
    themes_value = legacy_life_block.get("themes") or archetype.get("core_themes") or []
    if isinstance(themes_value, Sequence) and not isinstance(themes_value, str):
        themes_list = [clean_text(str(item)) for item in themes_value if isinstance(item, str)]
    elif isinstance(themes_value, str):
        themes_list = [clean_text(themes_value)]
    else:
        themes_list = []
    themes_list = [theme for theme in themes_list if theme]

    derived_from = legacy_life_block.get("derived_from")
    if not isinstance(derived_from, list):
        derived_from = []

    meta_payload = {
        "axis": legacy_life_block.get("axis") or archetype.get("dominant_axis"),
        "themes": themes_list,
        "focus": focus_value,
        "derived_from": derived_from,
        "confidence": legacy_life_block.get("confidence"),
        "correlations": correlations,
    }
    if not meta_payload["themes"]:
        meta_payload["themes"] = ["denge", "ifade", "farkındalık"]
    if not meta_payload["axis"]:
        meta_payload["axis"] = "Yay–İkizler"
    if not meta_payload["focus"]:
        meta_payload["focus"] = "içsel dengeyi hatırlamak"

    theme_line = ", ".join(meta_payload["themes"]) if meta_payload["themes"] else "Belirsiz"
    context_lines = [
        f"Eksen: {meta_payload.get('axis') or 'Belirtilmedi'}",
        f"Temalar: {theme_line}",
        f"Odak: {meta_payload.get('focus') or 'Belirtilmedi'}",
        f"Element dengesi: {correlations.get('element_balance') or 'Belirsiz'}",
        f"Modalite dengesi: {correlations.get('modality_balance') or 'Belirsiz'}",
        f"Baskın gezegen: {correlations.get('dominant_planet') or 'Belirsiz'}",
        f"Enerji deseni: {correlations.get('dominant_cluster') or 'Belirsiz'}",
        f"Polar eksen: {correlations.get('polar_axis') or 'Belirsiz'}",
    ]
    context_str = "\n".join(context_lines)

    try:
        life_story = enforce_style_or_rewrite(
            call_groq_ai,
            AI_PROMPT,
            context_str,
            tries=2,
        )
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Life narrative generation failed: %s", exc)
        life_story = fallback_life_story(meta_payload)

    response_body["meta"] = meta_payload
    response_body["life_narrative"] = life_story
    response_body["life_legacy"] = legacy_life_block

    return jsonify(response_body), 200
