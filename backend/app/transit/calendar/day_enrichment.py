from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

SIGN_TO_ELEMENT = {
    "Aries": "fire",
    "Taurus": "earth",
    "Gemini": "air",
    "Cancer": "water",
    "Leo": "fire",
    "Virgo": "earth",
    "Libra": "air",
    "Scorpio": "water",
    "Sagittarius": "fire",
    "Capricorn": "earth",
    "Aquarius": "air",
    "Pisces": "water",
}

TR_MOON_INGRESS_MAP = {
    "Koç": "Aries",
    "Boğa": "Taurus",
    "İkizler": "Gemini",
    "Yengeç": "Cancer",
    "Aslan": "Leo",
    "Başak": "Virgo",
    "Terazi": "Libra",
    "Akrep": "Scorpio",
    "Yay": "Sagittarius",
    "Oğlak": "Capricorn",
    "Kova": "Aquarius",
    "Balık": "Pisces",
}


def _infer_moon_sign_from_labels(labels: List[str]) -> Optional[str]:
    for lab in labels or []:
        if lab.startswith("Ay ") and " girişi" in lab:
            parts = lab.split()
            if len(parts) >= 2:
                tr_sign = parts[1]
                return TR_MOON_INGRESS_MAP.get(tr_sign)
    return None


def _derive_flags_from_event_ids(event_ids: List[str]) -> Dict[str, bool]:
    ids = event_ids or []
    joined = " ".join(ids)

    return {
        "venus_retro": ("phase.retro.Venus" in joined) or ("phase.station.Venus" in joined),
        "mars_retro": ("phase.retro.Mars" in joined) or ("phase.station.Mars" in joined),
        "mercury_retro": ("phase.retro.Mercury" in joined) or ("phase.station.Mercury" in joined),
        "eclipse": ("eclipse" in joined) or ("phase.eclipse" in joined),
        "moon_voc": ("moon.voc" in joined) or ("phase.voc.Moon" in joined),
        "moon_square_mars": ("tr.moon.square.mars" in joined),
        "moon_square_saturn": ("tr.moon.square.saturn" in joined),
    }


def enrich_calendar_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    days = payload.get("days", [])

    current_moon_sign = None
    for day in days:
        inferred = _infer_moon_sign_from_labels(day.get("labels", []))
        if inferred:
            current_moon_sign = inferred

        day["moon_sign"] = current_moon_sign
        day["moon_element"] = SIGN_TO_ELEMENT.get(current_moon_sign) if current_moon_sign else None

        event_ids: List[str] = []
        event_ids += day.get("top_event_ids", []) or []
        event_ids += day.get("phase_event_ids", []) or []
        event_ids += day.get("marker_ids", []) or []

        day["flags"] = _derive_flags_from_event_ids(event_ids)

    return payload
