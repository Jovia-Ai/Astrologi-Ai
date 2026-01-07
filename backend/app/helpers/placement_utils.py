"""Placement parsing helpers shared across engines."""
from __future__ import annotations

from typing import Dict, Iterable

from .normalize import normalize_planet_key, normalize_sign_key


def extract_planet_signs(
    placements: Iterable[str],
    *,
    strip_in_tokens: bool = True,
    drop_house_tokens: bool = True,
) -> Dict[str, str]:
    """
    placements: current placements structure (list of dicts)
    returns: {planet: sign}
    Must preserve behavior from:
      - dispositor_flow._extract_planet_signs
      - axis_activation._map_planets_to_signs
    """
    mapping: Dict[str, str] = {}
    for placement in placements:
        if "_in_" not in placement:
            continue
        if drop_house_tokens and "_house" in placement:
            continue
        planet, slug = placement.split("_in_", 1)
        planet_key = normalize_planet_key(planet)
        sign_token = slug.split("_")[0] if strip_in_tokens else slug
        sign_key = normalize_sign_key(sign_token)
        if not (planet_key and sign_key):
            continue
        mapping[planet_key] = sign_key
    return mapping
