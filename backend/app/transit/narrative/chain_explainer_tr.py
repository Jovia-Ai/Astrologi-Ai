from __future__ import annotations

from typing import Any, Mapping


def build_chain_explainer_tr(event: Mapping[str, Any], derived_context: Mapping[str, Any]) -> str:
    if not isinstance(event, Mapping) or not isinstance(derived_context, Mapping):
        return ""

    angle = derived_context.get("angle") if isinstance(derived_context.get("angle"), Mapping) else {}
    if not isinstance(angle, Mapping):
        return ""

    name = str(angle.get("name") or "").strip().upper()
    sign = str(angle.get("sign") or "").strip()
    ruler = str(angle.get("ruler") or "").strip()
    ruler_house = _safe_int(angle.get("ruler_house"))

    transit_body = str(event.get("transit_body") or "").strip().lower()
    aspect = str(event.get("aspect") or "").strip().lower()
    natal_point = str(event.get("natal_point") or "").strip().upper()
    links = derived_context.get("links") if isinstance(derived_context.get("links"), list) else []
    has_cofeatured = any(
        isinstance(link, Mapping)
        and str(link.get("type") or "").strip().lower() == "cofeatured_hit"
        for link in links
    )

    if transit_body == "neptune" and aspect == "square" and natal_point == "ASC":
        if sign and ruler and ruler_house:
            resonance = (
                " Aynı fazda Neptün-Satürn hattı da eşlik edince"
                if has_cofeatured
                else " Neptün aynı anda Satürn hattını da titreştirdiği için"
            )
            return (
                f"Yükselenin {sign}; yöneticisi {ruler} sende {ruler_house}. evde. "
                f"{resonance} "
                "sis ne dediğinden çok nasıl duyulduğun üzerinden çalışır."
            )
        return "Neptün burada söz ile algı arasına ince bir sis bırakır; net çerçeve şarttır."

    if name and sign and ruler:
        house_part = f"{ruler_house}. evde" if ruler_house else "kendi hattında"
        return f"{name} {sign}; yöneticisi {ruler} {house_part} çalışıyor."
    return ""


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
