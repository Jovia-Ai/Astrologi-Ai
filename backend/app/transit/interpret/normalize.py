from __future__ import annotations

ASPECT_NORM = {
    "conj": "conjunction",
    "conjunction": "conjunction",
    "square": "square",
    "sqr": "square",
    "opp": "opposition",
    "opposition": "opposition",
    "tri": "trine",
    "trine": "trine",
    "sex": "sextile",
    "sextile": "sextile",
}

OBJ_KEY_NORM = {
    "node": "North Node",
    "northnode": "North Node",
    "north node": "North Node",
    "n.node": "North Node",
    "nnode": "North Node",
    "true node": "North Node",
    "mean node": "North Node",
    "s.node": "South Node",
    "snode": "South Node",
    "southnode": "South Node",
    "south node": "South Node",
    "pof": "Fortune",
    "part of fortune": "Fortune",
    "fortune": "Fortune",
    "vertex": "Vertex",
}


def norm_aspect(aspect: str) -> str:
    a = (aspect or "").strip().lower()
    return ASPECT_NORM.get(a, aspect)


def canonical_obj_key(key: str) -> str:
    k = (key or "").strip()
    if not k:
        return k
    low = k.lower()
    return OBJ_KEY_NORM.get(low, k)
