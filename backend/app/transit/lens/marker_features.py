from __future__ import annotations


def infer_marker_features(marker: dict) -> dict:
    mid = (marker.get("id") or "").lower()
    label = (marker.get("label") or "").lower()

    flags = {
        "venus_retro": False,
        "mars_retro": False,
        "mercury_retro": False,
        "eclipse": False,
        "moon_voc": False,
        "moon_waxing": False,
        "moon_waning": False,
    }

    if "venus" in mid and "retro" in mid:
        flags["venus_retro"] = True
    if "mars" in mid and "retro" in mid:
        flags["mars_retro"] = True
    if "mercury" in mid and "retro" in mid:
        flags["mercury_retro"] = True

    if "eclipse" in mid or "tutul" in label:
        flags["eclipse"] = True

    if "void" in mid or "voc" in mid or "boşluk" in label:
        flags["moon_voc"] = True

    if "waxing" in mid or "büyüy" in label:
        flags["moon_waxing"] = True
    if "waning" in mid or "küçül" in label:
        flags["moon_waning"] = True

    return flags


def infer_bodies(marker: dict) -> list[str]:
    mid = (marker.get("id") or "")
    bodies: list[str] = []
    for body in [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "Chiron",
        "Node",
        "Fortune",
    ]:
        if body.lower() in mid.lower():
            bodies.append(body)
    return bodies
