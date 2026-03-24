from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Formatting helpers
# -----------------------------

ASPECT_LABEL_TR = {
    "conjunction": "☌ kavuşum",
    "trine": "△ üçgen",
    "square": "□ kare",
    "opposition": "☍ karşıt",
    "sextile": "✶ sekstil",
    "quincunx": "⚻ quincunx",
}

BODY_LABEL_TR = {
    "sun": "Güneş",
    "moon": "Ay",
    "mercury": "Merkür",
    "venus": "Venüs",
    "mars": "Mars",
    "jupiter": "Jüpiter",
    "saturn": "Satürn",
    "uranus": "Uranüs",
    "neptune": "Neptün",
    "pluto": "Plüton",
    "juno": "Juno",
    "node": "Ay Düğümü",
    "lilith": "Lilith",
    "chiron": "Chiron",
    "vertex": "Vertex",
    "fortune": "Fortuna",
    "asc": "ASC",
    "mc": "MC",
}


def _cap(s: str) -> str:
    if not s:
        return s
    return s[0].upper() + s[1:]


def _body_tr(body: str) -> str:
    return BODY_LABEL_TR.get(body, _cap(body))


def _aspect_tr(aspect: str) -> str:
    return ASPECT_LABEL_TR.get(aspect, aspect)


def _orb_text_from_deg(orb_deg: float) -> str:
    """
    Convert decimal degrees to D°M′, rounded to nearest minute.
    Example: 0.31° -> 0°19′
    """
    if orb_deg is None:
        return ""
    sign = "-" if orb_deg < 0 else ""
    x = abs(orb_deg)
    d = int(x)
    minutes = int(round((x - d) * 60))
    if minutes == 60:
        d += 1
        minutes = 0
    return f"{sign}{d}°{minutes:02d}′"


# -----------------------------
# Overlay utilities
# -----------------------------


def _group_overlay_by_house(overlay_table: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Input row example:
      {"body":"sun","formatted":"Capricorn 6°45′","in_house":4}
    Output:
      {"4":["sun","mercury"], "11":["moon"]}
    """
    out: Dict[str, List[str]] = {}
    for row in overlay_table or []:
        h = str(row.get("in_house"))
        b = row.get("body")
        if not h or not b:
            continue
        out.setdefault(h, []).append(b)
    # stable order
    for h in out:
        out[h] = sorted(out[h])
    return dict(sorted(out.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 999))


def _overlay_lines_tr(
    overlay_table: List[Dict[str, Any]],
    a_name: str,
    b_name: str,
    direction_label: str,
) -> List[str]:
    """
    "Sahra Güneş → Yiğit 4.ev (Capricorn 6°45′)"
    """
    lines: List[str] = []
    for row in overlay_table or []:
        body = row.get("body")
        in_house = row.get("in_house")
        formatted = row.get("formatted")
        if not body or not in_house:
            continue
        # Add a stable prefix for scanning
        lines.append(f"{direction_label} | {a_name} {_body_tr(body)} → {b_name} {in_house}.ev ({formatted})")
    return lines


def _overlay_by_house_lines_tr(
    by_house: Dict[str, List[str]],
    owner_name: str,
    incoming_name: str,
) -> List[str]:
    """
    "Yiğit 4.ev: Sahra Güneş, Merkür, Jüpiter"
    """
    lines: List[str] = []
    for h, bodies in (by_house or {}).items():
        pretty_bodies = ", ".join(_body_tr(b) for b in bodies)
        lines.append(f"Ev Özeti | {owner_name} {h}.ev: {incoming_name} {pretty_bodies}")
    return lines


# -----------------------------
# Aspect utilities
# -----------------------------


def _aspect_line_tr(a_body: str, b_body: str, aspect: str, orb_deg: float, a_name: str, b_name: str) -> str:
    orb_txt = _orb_text_from_deg(orb_deg)
    # More scannable:
    # "Açı: Ay ☌ Mars • orb 0°19′"
    return f"Açı: {_body_tr(a_body)} {_aspect_tr(aspect)} {_body_tr(b_body)} • orb {orb_txt}"


def _sort_key_aspect(hit: Dict[str, Any]) -> Tuple[int, float]:
    """
    Prefer tighter orb first. If missing, push down.
    """
    orb = hit.get("orb_deg")
    if orb is None:
        return (1, 999.0)
    return (0, float(orb))


# -----------------------------
# Touchpoints: aspect + overlay house context
# -----------------------------


def _overlay_house_lookup(overlay_by_body: Dict[str, Any]) -> Dict[str, int]:
    """
    overlay_by_body example: {"sun":4,"moon":11,...}
    """
    out: Dict[str, int] = {}
    for k, v in (overlay_by_body or {}).items():
        try:
            out[str(k)] = int(v)
        except Exception:
            continue
    return out


def _build_touchpoints(
    hits: List[Dict[str, Any]],
    a_in_b_by_body: Dict[str, Any],
    b_in_a_by_body: Dict[str, Any],
    a_name: str,
    b_name: str,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    a_house = _overlay_house_lookup(a_in_b_by_body)
    b_house = _overlay_house_lookup(b_in_a_by_body)
    rows: List[Dict[str, Any]] = []
    lines: List[str] = []

    for h in sorted(hits or [], key=_sort_key_aspect):
        a_body = h.get("a_body")
        b_body = h.get("b_body")
        aspect = h.get("aspect")
        orb = h.get("orb_deg")
        if not a_body or not b_body or not aspect:
            continue

        a_in_b_house = a_house.get(str(a_body))
        b_in_a_house = b_house.get(str(b_body))

        # keep only meaningful ones that have at least one house context
        if a_in_b_house is None and b_in_a_house is None:
            continue

        row = {
            "a_body": a_body,
            "b_body": b_body,
            "aspect": aspect,
            "orb_deg": orb,
            "orb_text": _orb_text_from_deg(float(orb)) if orb is not None else "",
            "a_in_b_house": a_in_b_house,
            "b_in_a_house": b_in_a_house,
        }
        rows.append(row)

        # Make it instantly readable: location + aspect separated
        loc_left = (
            f"{a_name} {_body_tr(a_body)} → {b_name} {a_in_b_house}.ev"
            if a_in_b_house is not None
            else f"{a_name} {_body_tr(a_body)}"
        )
        loc_right = (
            f"{b_name} {_body_tr(b_body)} → {a_name} {b_in_a_house}.ev"
            if b_in_a_house is not None
            else f"{b_name} {_body_tr(b_body)}"
        )
        orb_txt = row["orb_text"]
        # Single-line but structured:
        # "TP | Konum: A Ay→B 11.ev | B Mars→A 8.ev | Açı: Ay ☌ Mars • orb 0°19′"
        lines.append(
            f"TP | Konum: {loc_left} | {loc_right} | Açı: {_body_tr(a_body)} {_aspect_tr(aspect)} {_body_tr(b_body)} • orb {orb_txt}"
        )

    return rows, lines


# -----------------------------
# Public assembly
# -----------------------------


def build_synastry_public(
    engine_out: Dict[str, Any],
    partner_a_name: Optional[str] = None,
    partner_b_name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Takes engine output and returns public payload with:
      - meta names
      - tables (machine-friendly)
      - display (human-friendly lines)
    """
    a_name = partner_a_name or "Partner A"
    b_name = partner_b_name or "Partner B"

    public = dict(engine_out.get("public") or {})
    overlays = public.get("overlays") or {}
    debug = engine_out.get("debug") or {}

    a_in_b = overlays.get("a_in_b") or {}
    b_in_a = overlays.get("b_in_a") or {}

    a_in_b_table = a_in_b.get("table") or []
    b_in_a_table = b_in_a.get("table") or []
    a_in_b_by_body = a_in_b.get("by_body") or {}
    b_in_a_by_body = b_in_a.get("by_body") or {}

    # aspects source: debug.hits (already includes orb_deg, a_body, b_body, aspect)
    hits = debug.get("hits") or []

    # overlay by house groups
    a_in_b_by_house = _group_overlay_by_house(a_in_b_table)
    b_in_a_by_house = _group_overlay_by_house(b_in_a_table)

    # aspect top lines (sorted by orb) - more scannable, no repeated names
    aspect_lines_top = []
    aspect_rows_top = []
    for h in sorted(hits, key=_sort_key_aspect):
        a_body = h.get("a_body")
        b_body = h.get("b_body")
        aspect = h.get("aspect")
        orb = h.get("orb_deg")
        if not a_body or not b_body or not aspect or orb is None:
            continue
        aspect_rows_top.append(
            {
                "a_body": a_body,
                "b_body": b_body,
                "aspect": aspect,
                "orb_deg": orb,
                "orb_text": _orb_text_from_deg(float(orb)),
            }
        )
        aspect_lines_top.append(_aspect_line_tr(a_body, b_body, aspect, float(orb), a_name, b_name))

    # touchpoints (aspect + overlay house context)
    touch_rows, touch_lines = _build_touchpoints(
        hits=hits,
        a_in_b_by_body=a_in_b_by_body,
        b_in_a_by_body=b_in_a_by_body,
        a_name=a_name,
        b_name=b_name,
    )

    # display overlay lines
    overlay_lines_a_in_b = _overlay_lines_tr(a_in_b_table, a_name, b_name, "A→B")
    overlay_lines_b_in_a = _overlay_lines_tr(b_in_a_table, b_name, a_name, "B→A")
    overlay_lines_by_house_a_in_b = _overlay_by_house_lines_tr(a_in_b_by_house, b_name, a_name)
    overlay_lines_by_house_b_in_a = _overlay_by_house_lines_tr(b_in_a_by_house, a_name, b_name)

    public["meta"] = {
        "partner_a_name": a_name,
        "partner_b_name": b_name,
    }

    public["tables"] = {
        "overlays": {
            "a_in_b": a_in_b_table,
            "b_in_a": b_in_a_table,
            "a_in_b_by_house": a_in_b_by_house,
            "b_in_a_by_house": b_in_a_by_house,
        },
        "aspects": {
            "top": aspect_rows_top,  # UI can slice first N
        },
        "touchpoints": touch_rows,
    }

    public["display"] = {
        "overlays_lines": {
            "a_in_b": overlay_lines_a_in_b,
            "b_in_a": overlay_lines_b_in_a,
            "by_house_a_in_b": overlay_lines_by_house_a_in_b,
            "by_house_b_in_a": overlay_lines_by_house_b_in_a,
        },
        "aspects_lines": {
            "top": aspect_lines_top,
        },
        "touchpoints_lines": touch_lines,
    }

    out = dict(engine_out)
    out["public"] = public
    return out
