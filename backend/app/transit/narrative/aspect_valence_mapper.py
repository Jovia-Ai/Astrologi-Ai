from __future__ import annotations

from enum import Enum
from typing import Any


class ValenceMode(str, Enum):
    TENSION = "tension"
    OPENING = "opening"
    MATURATION = "maturation"
    RELEASE = "release"
    INTEGRATION = "integration"
    RECOGNITION = "recognition"
    MOMENTUM = "momentum"


class IntensityMode(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    DENSE = "dense"


PLANET_PAIR_CLASS_TABLE: dict[tuple[str, str], str] = {
    ("Mars", "Saturn"): "structuring_action_pair",
    ("Saturn", "Mars"): "structuring_action_pair",
    ("Venus", "Jupiter"): "expansive_pair",
    ("Jupiter", "Venus"): "expansive_pair",
    ("Sun", "Moon"): "self_integration_pair",
    ("Moon", "Sun"): "self_integration_pair",
    ("Mars", "Pluto"): "power_pair",
    ("Pluto", "Mars"): "power_pair",
    ("Saturn", "Mars"): "structuring_action_pair",
    ("Mars", "Saturn"): "structuring_action_pair",
    ("Sun", "Jupiter"): "expansion_pair",
    ("Jupiter", "Sun"): "expansion_pair",
    ("Sun", "Mars"): "activation_pair",
    ("Mars", "Sun"): "activation_pair",
    ("Venus", "Pluto"): "transformation_pair",
    ("Pluto", "Venus"): "transformation_pair",
    ("Mercury", "Saturn"): "structuring_thought_pair",
    ("Saturn", "Mercury"): "structuring_thought_pair",
    ("Sun", "Saturn"): "authority_construction_pair",
    ("Saturn", "Sun"): "authority_construction_pair",
    ("Sun", "MC"): "visibility_pair",
    ("Jupiter", "MC"): "visibility_pair",
    ("Venus", "MC"): "visibility_pair",
    ("Mars", "MC"): "activation_pair",
    ("MC", "Sun"): "visibility_pair",
    ("MC", "Jupiter"): "visibility_pair",
    ("MC", "Venus"): "visibility_pair",
    ("MC", "Mars"): "activation_pair",
    ("North Node", "South Node"): "axis_integration_pair",
    ("South Node", "North Node"): "axis_integration_pair",
    ("North Node", "ASC"): "axis_integration_pair",
    ("ASC", "North Node"): "axis_integration_pair",
}

ASPECT_INTENSITY_TABLE: dict[str, IntensityMode] = {
    "trine": IntensityMode.LIGHT,
    "sextile": IntensityMode.MEDIUM,
    "conjunction": IntensityMode.DENSE,
    "square": IntensityMode.DENSE,
    "opposition": IntensityMode.DENSE,
    "quincunx": IntensityMode.MEDIUM,
    "semi_sextile": IntensityMode.LIGHT,
}

PAIR_INTENSITY_OVERRIDE: dict[tuple[str, str], IntensityMode] = {
    ("power_pair", "trine"): IntensityMode.DENSE,
    ("activation_pair", "trine"): IntensityMode.MEDIUM,
    ("visibility_pair", "sextile"): IntensityMode.LIGHT,
    ("structuring_action_pair", "sextile"): IntensityMode.MEDIUM,
}

PAIR_ASPECT_VALENCE: dict[tuple[str, str], ValenceMode] = {
    ("expansive_pair", "square"): ValenceMode.INTEGRATION,
    ("expansive_pair", "opposition"): ValenceMode.INTEGRATION,
    ("expansive_pair", "trine"): ValenceMode.OPENING,
    ("expansive_pair", "sextile"): ValenceMode.OPENING,
    ("self_integration_pair", "square"): ValenceMode.INTEGRATION,
    ("self_integration_pair", "opposition"): ValenceMode.INTEGRATION,
    ("self_integration_pair", "conjunction"): ValenceMode.INTEGRATION,
    ("power_pair", "trine"): ValenceMode.MOMENTUM,
    ("power_pair", "sextile"): ValenceMode.MOMENTUM,
    ("power_pair", "square"): ValenceMode.TENSION,
    ("power_pair", "opposition"): ValenceMode.TENSION,
    ("structuring_action_pair", "sextile"): ValenceMode.MATURATION,
    ("structuring_action_pair", "trine"): ValenceMode.MATURATION,
    ("structuring_action_pair", "square"): ValenceMode.TENSION,
    ("authority_construction_pair", "conjunction"): ValenceMode.MATURATION,
    ("authority_construction_pair", "square"): ValenceMode.MATURATION,
    ("expansion_pair", "trine"): ValenceMode.RECOGNITION,
    ("expansion_pair", "sextile"): ValenceMode.OPENING,
    ("activation_pair", "conjunction"): ValenceMode.MOMENTUM,
    ("activation_pair", "trine"): ValenceMode.MOMENTUM,
    ("transformation_pair", "square"): ValenceMode.INTEGRATION,
    ("transformation_pair", "opposition"): ValenceMode.INTEGRATION,
    ("structuring_thought_pair", "square"): ValenceMode.MATURATION,
    ("structuring_thought_pair", "sextile"): ValenceMode.MATURATION,
    ("visibility_pair", "trine"): ValenceMode.RECOGNITION,
    ("visibility_pair", "sextile"): ValenceMode.RECOGNITION,
    ("visibility_pair", "conjunction"): ValenceMode.RECOGNITION,
    ("visibility_pair", "square"): ValenceMode.MOMENTUM,
    ("axis_integration_pair", "opposition"): ValenceMode.INTEGRATION,
    ("axis_integration_pair", "square"): ValenceMode.INTEGRATION,
    ("axis_integration_pair", "trine"): ValenceMode.MOMENTUM,
}

_SOFT_ASPECTS = {"trine", "sextile", "semi_sextile"}
_BENEFIC_POINTS = {"Venus", "Jupiter", "Sun", "Moon", "MC", "ASC", "North Node"}
_IDENTITY_POINTS = {"Sun", "Moon", "ASC", "MC", "North Node", "South Node"}
_RELEASE_POINTS = {"Neptune", "South Node"}


def classify_planet_pair(planet_a: str, planet_b: str) -> str:
    pair = (_normalize_point(planet_a), _normalize_point(planet_b))
    return PLANET_PAIR_CLASS_TABLE.get(pair, "unclassified")


def aspect_to_intensity(aspect_type: str) -> IntensityMode:
    return ASPECT_INTENSITY_TABLE.get(str(aspect_type or "").strip().lower(), IntensityMode.MEDIUM)


def aspect_to_valence(pair_class: str, aspect_type: str) -> ValenceMode:
    return PAIR_ASPECT_VALENCE.get(
        (str(pair_class or "").strip(), str(aspect_type or "").strip().lower()),
        ValenceMode.INTEGRATION,
    )


def derive_valence_intensity(
    *,
    transit_body: str,
    natal_point: str,
    aspect_type: str,
    chapter_role: str,
    natal_backing: bool,
    event_nature: str = "",
) -> tuple[ValenceMode, IntensityMode, dict[str, Any]]:
    planet_a = _normalize_point(transit_body)
    planet_b = _normalize_point(natal_point)
    pair_class = classify_planet_pair(planet_a, planet_b)
    aspect = str(aspect_type or "").strip().lower()
    intensity = aspect_to_intensity(aspect)
    intensity_source = "aspect_default"
    override = PAIR_INTENSITY_OVERRIDE.get((pair_class, aspect))
    if override is not None:
        intensity = override
        intensity_source = "pair_override"
    elif aspect == "sextile" and (planet_a in _RELEASE_POINTS or planet_b in _RELEASE_POINTS):
        intensity = IntensityMode.LIGHT
        intensity_source = "release_soft_override"

    valence_source = "pair_aspect"
    fallback_used = False
    if pair_class == "unclassified":
        valence = _fallback_valence(
            planet_a=planet_a,
            planet_b=planet_b,
            aspect_type=aspect,
            intensity=intensity,
        )
        valence_source = "fallback"
        fallback_used = True
    else:
        valence = aspect_to_valence(pair_class, aspect)

    bias_notes: list[str] = []
    role = str(chapter_role or "").strip().lower()
    event = str(event_nature or "").strip().lower()

    if role == "release" and intensity != IntensityMode.DENSE and (event == "dissolution" or planet_a in _RELEASE_POINTS):
        valence = ValenceMode.RELEASE
        bias_notes.append("chapter_role_release_bias")
    elif planet_a == "Saturn" and intensity == IntensityMode.DENSE and event == "responsibility":
        valence = ValenceMode.MATURATION
        bias_notes.append("saturn_dense_responsibility_bias")
    elif planet_a == "Saturn" and intensity == IntensityMode.DENSE and event == "boundary":
        valence = ValenceMode.TENSION
        bias_notes.append("saturn_dense_boundary_bias")
    elif role == "peak" and valence == ValenceMode.OPENING and pair_class in {"visibility_pair", "expansion_pair"}:
        valence = ValenceMode.RECOGNITION
        bias_notes.append("chapter_role_peak_visibility_bias")
    elif role == "builder" and valence == ValenceMode.OPENING and planet_a in {"Saturn", "Mercury"}:
        valence = ValenceMode.MATURATION
        bias_notes.append("chapter_role_builder_structure_bias")

    if natal_backing and valence == ValenceMode.TENSION and pair_class in {"self_integration_pair", "axis_integration_pair"}:
        valence = ValenceMode.INTEGRATION
        bias_notes.append("natal_backing_self_integration_bias")

    debug = {
        "planet_pair": [planet_a, planet_b],
        "pair_class": pair_class,
        "aspect_type": aspect,
        "valence_source": valence_source,
        "intensity_source": intensity_source,
        "fallback_used": fallback_used,
        "bias_notes": bias_notes,
    }
    return valence, intensity, debug


def _fallback_valence(
    *,
    planet_a: str,
    planet_b: str,
    aspect_type: str,
    intensity: IntensityMode,
) -> ValenceMode:
    points = {planet_a, planet_b}
    aspect = str(aspect_type or "").strip().lower()
    if intensity == IntensityMode.DENSE:
        if points & _RELEASE_POINTS:
            return ValenceMode.RELEASE
        if points <= _IDENTITY_POINTS or points & _BENEFIC_POINTS:
            return ValenceMode.INTEGRATION
        return ValenceMode.TENSION
    if intensity == IntensityMode.LIGHT:
        if points & {"Sun", "Jupiter", "Venus", "MC"}:
            return ValenceMode.OPENING
        return ValenceMode.RELEASE if points & _RELEASE_POINTS else ValenceMode.OPENING
    if aspect in _SOFT_ASPECTS and points & {"Saturn", "Mercury"}:
        return ValenceMode.MATURATION
    return ValenceMode.INTEGRATION


def _normalize_point(value: str) -> str:
    token = str(value or "").strip()
    if not token:
        return ""
    lowered = token.lower().replace("-", " ").replace("_", " ")
    aliases = {
        "asc": "ASC",
        "dsc": "DSC",
        "mc": "MC",
        "ic": "IC",
        "north node": "North Node",
        "northnode": "North Node",
        "south node": "South Node",
        "southnode": "South Node",
    }
    if lowered in aliases:
        return aliases[lowered]
    return token[:1].upper() + token[1:].lower()
