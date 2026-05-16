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
* ``dispositor_chains`` and aspect applying/separating are now
  implemented (PR-1b) by delegating to the existing, fully-read
  ``dispositor_engine.build_dispositor_chain`` and
  ``aspect_direction.compute_direction`` — no contract guessing.
* ``chart_shape`` remains intentionally out of scope (non-trivial;
  not half-implemented).

This module mutates no global state and is not wired into any pipeline.
Wiring into ``_prepare_payload_from_chart`` is PR-3 (contract plumbing).
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

from app.astro.aspect_direction import compute_direction
from app.astro.dignity import RULERSHIPS, essential_dignity
from app.natal.dispositor_engine import build_dispositor_chain

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


# --------------------------------------------------------------------------
# PR-2a — Half-B salience scaffold (spec §2.2). UNCALIBRATED: starting
# weights only. 2 charts cannot calibrate, only test directionality.
# Carried as data flag `_uncalibrated: true` so no consumer mistakes
# scaffold tiers for truth. Pipeline-untouched; consumed only by scorer.
# --------------------------------------------------------------------------

_SAL_BASE = {"luminary": 0.30, "chart_ruler": 0.24, "mc_ruler": 0.18,
             "stellium": 0.20, "angular": 0.16, "plain": 0.10,
             "aspect": 0.18}
_SAL_DIGNITY = {"domicile": 0.12, "exaltation": 0.10,
                "detriment": 0.06, "fall": 0.06, "peregrine": 0.0}
_SAL_TIGHTNESS = ((1.0, 0.12), (3.0, 0.08), (6.0, 0.04))
_SAL_TIERS = {"defining": 0.42, "strong": 0.30}
_ANGULAR_H = {1, 4, 7, 10}
_SUCCEDENT_H = {2, 5, 8, 11}


def _sal_tier(score: float | None) -> str | None:
    if score is None:
        return None
    if score >= _SAL_TIERS["defining"]:
        return "defining"
    if score >= _SAL_TIERS["strong"]:
        return "strong"
    return "background"


def _planet_salience(name: str, skel: Mapping[str, Any]) -> float | None:
    dt = {_norm(r["planet"]): r for r in skel.get("dignity_table", [])}
    row = dt.get(_norm(name))
    if not row:
        return None
    house = row.get("house")
    dignity = _norm(row.get("dignity"))
    asc = skel.get("asc_ruler_spine", {})
    mc = skel.get("mc_ruler_spine", {})
    is_cr = _norm(asc.get("ruler")) == _norm(name)
    is_mcr = _norm(mc.get("ruler")) == _norm(name)
    is_lum = _norm(name) in ("sun", "moon")
    in_stel = [s for s in skel.get("stelliums", [])
               if _norm(name) in {_norm(p) for p in s.get("planets", [])}]
    is_ang = isinstance(house, int) and house in _ANGULAR_H

    roles = [_SAL_BASE["plain"]]
    if is_lum:
        roles.append(_SAL_BASE["luminary"])
    if is_cr:
        roles.append(_SAL_BASE["chart_ruler"])
    if is_mcr:
        roles.append(_SAL_BASE["mc_ruler"])
    if in_stel:
        roles.append(_SAL_BASE["stellium"])
    if is_ang:
        roles.append(_SAL_BASE["angular"])
    s = max(roles)

    s += _SAL_DIGNITY.get(dignity, 0.0)

    if isinstance(house, int):
        if house in _ANGULAR_H:
            s += 0.10
        elif house in _SUCCEDENT_H:
            s += 0.04

    if in_stel:
        big = any(int(st.get("count", 0)) >= 4 for st in in_stel)
        s += 0.12 if big else 0.08

    orbs = [a["orb"] for a in skel.get("tightest_aspects", [])
            if _norm(name) in (_norm(a.get("a")), _norm(a.get("b")))]
    if orbs:
        mo = min(orbs)
        for lim, val in _SAL_TIGHTNESS:
            if mo <= lim:
                s += val
                break

    if is_cr:
        if is_ang and dignity in ("domicile", "exaltation"):
            s += 0.10
        elif dignity in ("detriment", "fall"):
            s += 0.04

    return round(s, 3)


def _enrich_with_salience(skel: dict[str, Any]) -> None:
    """Mutate skel in place: add salience / salience_tier (UNCALIBRATED)."""
    psal: dict[str, float] = {}
    for row in skel.get("dignity_table", []):
        v = _planet_salience(row["planet"], skel)
        if v is None:
            continue
        psal[_norm(row["planet"])] = v
        row["salience"] = v
        row["salience_tier"] = _sal_tier(v)
    for key in ("sun", "moon"):
        lum = skel.get("luminaries", {}).get(key)
        if lum is not None:
            v = psal.get(key)
            lum["salience"] = v
            lum["salience_tier"] = _sal_tier(v)
    for spine_key in ("asc_ruler_spine", "mc_ruler_spine"):
        sp = skel.get(spine_key, {})
        v = psal.get(_norm(sp.get("ruler")))
        sp["ruler_salience"] = v
        sp["ruler_salience_tier"] = _sal_tier(v)
    for st in skel.get("stelliums", []):
        v = round(_SAL_BASE["stellium"]
                  + (0.12 if int(st.get("count", 0)) >= 4 else 0.08), 3)
        st["salience"] = v
        st["salience_tier"] = _sal_tier(v)
    for a in skel.get("tightest_aspects", []):
        v = _SAL_BASE["aspect"]
        orb = a.get("orb")
        if isinstance(orb, (int, float)):
            for lim, val in _SAL_TIGHTNESS:
                if orb <= lim:
                    v += val
                    break
        v = round(v, 3)
        a["salience"] = v
        a["salience_tier"] = _sal_tier(v)
    skel["_salience_meta"] = {
        "_uncalibrated": True,
        "note": ("PR-2a scaffold: spec §2.2 starting weights. Two "
                 "reference charts test directionality only, NOT "
                 "calibration. Weights/tiers provisional until the "
                 "stratified corpus calibrates them."),
        "tiers": dict(_SAL_TIERS),
    }


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
    # Only true planet-planet aspects. Excludes angle-axis self-pairs
    # (Asc↔Desc, MC↔IC are structurally always 0°/180°) and derived
    # points (Vertex/Fortune/Node — this engine duplicates Vertex onto
    # Venus's longitude). An astrologer never calls Asc-Desc a "tight
    # aspect"; surfaced by the ARC corpus on day one.
    _planet_set = {p.lower() for p in _DIGNITY_PLANETS}
    sortable = [
        a for a in aspects
        if isinstance(a, Mapping)
        and isinstance(a.get("orb"), (int, float))
        and _norm(a.get("planet1")) in _planet_set
        and _norm(a.get("planet2")) in _planet_set
    ]
    sortable.sort(key=lambda a: float(a["orb"]))
    tightest_aspects: list[dict[str, Any]] = []
    for a in sortable[:_TIGHTEST_ASPECT_COUNT]:
        a_name, b_name = a.get("planet1"), a.get("planet2")
        a_p = _planet_lookup(planets, a_name)
        b_p = _planet_lookup(planets, b_name)
        atype = a.get("aspect") or a.get("type")
        # "direction" holds the richer aspect_direction enum
        # ("applying" | "separating" | "exact" | None) rather than a bool.
        direction = compute_direction(
            str(atype or ""),
            a_p.get("longitude"),
            b_p.get("longitude"),
            a_p.get("speed"),
            b_p.get("speed"),
        )
        tightest_aspects.append({
            "a": a_name,
            "b": b_name,
            "type": atype,
            "orb": round(float(a["orb"]), 2),
            "direction": direction,
        })

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

    # --- dispositor chains (delegated to dispositor_engine) -----------
    dispositor_chains: list[dict[str, Any]] = []
    for name in _DIGNITY_PLANETS:
        if not _planet_lookup(planets, name):
            continue
        chain = build_dispositor_chain(name, chart_data)
        dispositor_chains.append({
            "planet": name,
            "start_sign": chain.get("start_sign"),
            "primary_chain": chain.get("primary_chain", []),
            "termination_reason": chain.get("termination_reason"),
        })

    skel = {
        "schema": "arc_chart_skeleton_v0_1",
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
        "dispositor_chains": dispositor_chains,
        "_deferred": [
            "salience CALIBRATION (corpus-blocked; weights UNCALIBRATED)",
            "chart_shape (non-trivial; not half-implemented)",
        ],
    }
    _enrich_with_salience(skel)  # PR-2a Half-B (UNCALIBRATED scaffold)
    return skel
