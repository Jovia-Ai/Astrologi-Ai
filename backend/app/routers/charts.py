"""Chart-related HTTP routes."""
from __future__ import annotations

import logging
from typing import Mapping

from flask import Blueprint, jsonify, request

from app.ai.narrative.formatter import (
    build_formatted_aspects,
    build_formatted_house_positions,
    build_formatted_planet_positions,
)
from app.ai.narrative.groq_client import (
    chart_to_summary,
    generate_ai_interpretation,
    generate_synastry_interpretation,
)
from app.astro.chart_engine.builder import build_natal_chart
from app.astro.synastry.cross_aspects import calculate_synastry_aspects
from app.models.user import BirthDataSchema
from app.core.config import settings
from app.core.errors import AIError, ApiError
from app.services.profiles import save_birth_data

charts_bp = Blueprint("charts", __name__)
logger = logging.getLogger(__name__)


def _handle_natal_chart_request():
    try:
        payload = request.get_json(force=True) or {}
        chart = build_natal_chart(payload)
        summary = chart_to_summary(chart)
        chart["interpretation"] = generate_ai_interpretation(summary)
        chart["formatted_positions"] = build_formatted_planet_positions(chart)
        chart["formatted_houses"] = build_formatted_house_positions(chart)
        chart["formatted_aspects"] = build_formatted_aspects(chart)
    except ApiError as exc:
        logger.error("External API error: %s", exc)
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to calculate natal chart")
        return jsonify({"error": str(exc)}), 400
    return jsonify(chart)


@charts_bp.route("/api/calculate-natal-chart", methods=["POST", "OPTIONS"])
@charts_bp.route("/natal-chart", methods=["POST", "OPTIONS"])
def calculate_natal_chart():
    if request.method == "OPTIONS":
        return "", 204
    return _handle_natal_chart_request()


@charts_bp.route("/api/calculate-synastry", methods=["POST", "OPTIONS"])
@charts_bp.route("/calculate_synastry_chart", methods=["POST", "OPTIONS"])
def calculate_synastry():
    if request.method == "OPTIONS":
        return "", 204
    try:
        payload = request.get_json(force=True) or {}
        person1 = payload.get("person1")
        person2 = payload.get("person2")
        if not isinstance(person1, Mapping) or not isinstance(person2, Mapping):
            raise ValueError("person1 and person2 must be objects containing birth date and city information.")
        chart1 = build_natal_chart(person1)
        chart2 = build_natal_chart(person2)
        aspects = calculate_synastry_aspects(chart1["planets"], chart2["planets"])
        response = {
            "person1": chart1,
            "person2": chart2,
            "aspects": aspects,
        }
        if settings.groq_api_key:
            try:
                response["interpretation"] = generate_synastry_interpretation(chart1, chart2, aspects)
            except AIError as exc:
                logger.warning("Synastry interpretation failed: %s", exc)
                response["interpretation_error"] = str(exc)
    except ApiError as exc:
        logger.error("External API error: %s", exc)
        return jsonify({"error": str(exc)}), 502
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to calculate synastry")
        return jsonify({"error": str(exc)}), 400
    return jsonify(response)


@charts_bp.route("/save-birth-data", methods=["POST"])
def save_birth_data_route():
    payload = BirthDataSchema(**(request.get_json(force=True) or {}))
    result = save_birth_data(
        user_id=payload.user_id,
        birth_date=payload.birth_date,
        birth_time=payload.birth_time,
        timezone=payload.timezone,
        place=payload.place,
        lat=payload.latitude,
        lon=payload.longitude,
    )
    return jsonify({"status": "ok", "saved": result})
