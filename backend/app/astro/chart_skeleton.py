"""ARC v0.1 — Layer 0 chart_skeleton extraction (PR-1, Half A only).

Deterministic chart-skeleton extraction. Pure function, no side effects,
no pipeline wiring. Consumes the structured ``chart_data`` returned by
``app.services.chart_service.compute_natal_chart`` /
``app.astro.chart_engine.builder.build_natal_chart``.

Scope (PR-1, deliberately narrow — see
``docs/system/arc_v0_1_layer0_pr_plan.md``):

* Produces ONLY the deterministic half (spec §2.1) of ``chart_skeleton``.
* Salience scoring (spec §2.2, Half B) is intentionally NOT here — it is
  PR-2 and is corpus-blocked.
* ``dispositor_chains`` and aspect applying/separating direction are
  intentionally DEFERRED (their producing functions —
  ``dispositor_engine.build_dispositor_chain`` and
  ``aspect_direction.compute_direction`` — must be read in full before
  being called; guessing their contract is rejected by repo policy).
  They are emitted as empty with an explicit ``_deferred`` marker.

This module mutates no global state and is not wired into any pipeline.
Wiring into ``_prepare_payload_from_chart`` is PR-3 (contract plumbing).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.astro.dignity import RULERSHIPS, essential_dignity

# Classical + modern planets carried in the dignity table. Points
# (North Node / Lilith / Vertex / Fortune) are excluded from dignity to
# avoid peregrine-noise; they may enter later layers if needed.
_DIGNITY_PLANETS: tuple[str, ...] = (
    "Sun", "Moon", "Mercury", "Venus", "Mars",
    "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto",
)

_LUMINARIES: tuple[str, ...] = ("Sun", "Moon")

_ANGULAR_HOUSES: frozenset[int] = frozenset({1, 4, 7, 10})

_ELEMENT_BY_SIGN: Mapping[str, str] = {
    "aries": "fire", "leo": "fire", "sagittarius": "fire",
    "taurus": "earth", "virgo": "earth", "capricorn": "earth",
    "gemini": "air", "libra": "air", "aquarius": "air",
    "cancer": "water", "scorpio": "water", "pisces": "water",
}

_MODALITY_BY_SIGN: Mapping[str, str] = {
    "aries": "cardinal", "cancer": "cardinal", "libra": "cardinal",
    "capricorn": "cardinal",
    "taurus": "fixed", "leo": "fixed", "scorpio": "fixed",
    "aquarius": "fixed",
    "gemini": "mutable", "virgo": "mutable", "sagittarius": "mutable",
    "pisces": "mutable",
}

_STELLIUM_MIN = 3
_TIGHTEST_ASPECT_COUNT = 5


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _ruler_of_sign(sign: str | None) -> str | None:
    """Return the planet that rules ``sign`` (traditional preferred).

    Derived by inverting ``app.astro.dignity.RULERSHIPS`` so we reuse the
    single source of truth rather than redefining a rulership table.
    Traditional rulers win over modern co-rulers when both exist.
    """
    s = _norm(sign)
    if not s:
        return None
    modern = {"uranus", "neptune", "pluto"}
    traditional_hit: str | None = None
    modern_hit: str | None = None
    for planet, signs in RULERSHIPS.items():
        if s in tuple(signs):
            if planet in modern:
                modern_hit = modern_hit or planet
            else:
                traditional_hit = traditional_hit or planet
    return traditional_hit or modern_hit


def _planet_lookup(planets: Mapping[str, Any], planet_name: str | None) -> dict[str, Any]:
    if not planet_name:
        return {}
    for name, payload in planets.items():
        if _norm(name) == _norm(planet_name) and isinstance(payload, Mapping):
            return dict(payload)
    return {}


def _ruler_spine(angle_sign: str | None, planets: Mapping[str, Any]) -> dict[str, Any]:
    ruler = _ruler_of_sign(angle_sign)
    ruler_title = ruler.title() if ruler else None
    rp = _planet_lookup(planets, ruler_title)
    return {
        "sign": angle_sign,
        "ruler": ruler_title,
        "ruler_sign": rp.get("sign"),
        "ruler_house": rp.get("house"),
        "ruler_dignity": (
            essential_dignity(ruler_title, rp.get("sign")) if rp else None
        ),
    }


def _tightest_aspect_for(planet_name: str, aspects: Sequence[Any]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for asp in aspects:
        if not isinstance(asp, Mapping):
            continue
        p1, p2 = _norm(asp.get("planet1")), _norm(asp.get("planet2"))
        if _norm(planet_name) not in (p1, p2):
            continue
        orb = asp.get("orb")
        if not isinstance(orb, (int, float)):
            continue
        if best is None or orb < best["orb"]:
            best = {
                "a": asp.get("planet1"),
                "b": asp.get("planet2"),
                "type": asp.get("aspect") or asp.get("type"),
                "orb": round(float(orb), 2),
            }
    return best


def build_chart_skeleton(chart_data: Mapping[str, Any]) -> dict[str, Any]:
    """Extract the deterministic chart_skeleton (spec §2.1, Half A).

    Returns a plain dict. Never raises on partial data — missing inputs
    degrade to empty/None rather than failing.
    """
    planets: Mapping[str, Any] = chart_data.get("planets") or {}
    angles: Mapping[str, Any] = chart_data.get("angles") or {}
    aspects: Sequence[Any] = chart_data.get("aspects") or []

    # --- meta: element / modality / sect -------------------------------
    elem = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    modal = {"cardinal": 0, "fixed": 0, "mutable": 0}
    for name in _DIGNITY_PLANETS:
        p = _planet_lookup(planets, name)
        sign = _norm(p.get("sign"))
        if sign in _ELEMENT_BY_SIGN:
            elem[_ELEMENT_BY_SIGN[sign]] += 1
        if sign in _MODALITY_BY_SIGN:
            modal[_MODALITY_BY_SIGN[sign]] += 1
    dominant_element = max(elem, key=elem.get) if any(elem.values()) else None
    lacking_element = min(elem, key=elem.get) if any(elem.values()) else None

    sun = _planet_lookup(planets, "Sun")
    sun_house = sun.get("house")
    # Day chart: Sun above the horizon (houses 7–12). Conservative default.
    sect = "unspecified"
    if isinstance(sun_house, int):
        sect = "day" if 7 <= sun_house <= 12 else "night"

    # --- luminaries ----------------------------------------------------
    luminaries: dict[str, Any] = {}
    for lum in _LUMINARIES:
        p = _planet_lookup(planets, lum)
        luminaries[lum.lower()] = {
            "sign": p.get("sign"),
            "house": p.get("house"),
            "dignity": essential_dignity(lum, p.get("sign")) if p else None,
            "tightest_aspect": _tightest_aspect_for(lum, aspects),
        }

    # --- asc / mc ruler spine -----------------------------------------
    asc_ruler_spine = _ruler_spine(angles.get("ascendant_sign"), planets)
    mc_ruler_spine = _ruler_spine(angles.get("midheaven_sign"), planets)

    # --- angular planets ----------------------------------------------
    angular_planets: list[dict[str, Any]] = []
    for name in _DIGNITY_PLANETS:
        p = _planet_lookup(planets, name)
        house = p.get("house")
        if isinstance(house, int) and house in _ANGULAR_HOUSES:
            angular_planets.append({
                "planet": name,
                "house": house,
                "sign": p.get("sign"),
                "dignity": essential_dignity(name, p.get("sign")),
            })

    # --- dignity table -------------------------------------------------
    dignity_table: list[dict[str, Any]] = []
    for name in _DIGNITY_PLANETS:
        p = _planet_lookup(planets, name)
        if not p:
            continue
        dignity_table.append({
            "planet": name,
            "sign": p.get("sign"),
            "house": p.get("house"),
            "dignity": essential_dignity(name, p.get("sign")),
        })

    # --- tightest aspects (global top-N by orb) -----------------------
    sortable = [
        a for a in aspects
        if isinstance(a, Mapping) and isinstance(a.get("orb"), (int, float))
    ]
    sortable.sort(key=lambda a: float(a["orb"]))
    tightest_aspects = [
        {
            "a": a.get("planet1"),
            "b": a.get("planet2"),
            "type": a.get("aspect") or a.get("type"),
            "orb": round(float(a["orb"]), 2),
            # applying/separating DEFERRED — see module docstring.
            "applying": None,
        }
        for a in sortable[:_TIGHTEST_ASPECT_COUNT]
    ]

    # --- stelliums (>=3 by sign or by house) --------------------------
    by_sign: dict[str, list[str]] = {}
    by_house: dict[int, list[str]] = {}
    for name in _DIGNITY_PLANETS:
        p = _planet_lookup(planets, name)
        sign = p.get("sign")
        house = p.get("house")
        if sign:
            by_sign.setdefault(str(sign), []).append(name)
        if isinstance(house, int):
            by_house.setdefault(house, []).append(name)
    stelliums: list[dict[str, Any]] = []
    for sign, members in by_sign.items():
        if len(members) >= _STELLIUM_MIN:
            stelliums.append({"by": "sign", "key": sign,
                              "planets": members, "count": len(members)})
    for house, members in by_house.items():
        if len(members) >= _STELLIUM_MIN:
            stelliums.append({"by": "house", "key": str(house),
                              "planets": members, "count": len(members)})

    return {
        "schema": "arc_chart_skeleton_v0_1_half_a",
        "meta": {
            "element_distribution": elem,
            "modality_distribution": modal,
            "dominant_element": dominant_element,
            "lacking_element": lacking_element,
            "sect": sect,
            "chart_shape": "unspecified",  # DEFERRED (non-trivial; not half-done)
        },
        "luminaries": luminaries,
        "asc_ruler_spine": asc_ruler_spine,
        "mc_ruler_spine": mc_ruler_spine,
        "angular_planets": angular_planets,
        "dignity_table": dignity_table,
        "tightest_aspects": tightest_aspects,
        "stelliums": stelliums,
        "dispositor_chains": [],  # DEFERRED — see module docstring
        "_deferred": [
            "salience_scoring (PR-2, corpus-blocked)",
            "dispositor_chains (needs full read of build_dispositor_chain)",
            "aspect applying/separating (needs full read of compute_direction)",
            "chart_shape (non-trivial; not half-implemented)",
        ],
    }
