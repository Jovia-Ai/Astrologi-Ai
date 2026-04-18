"""Aspect orb policy — paylaşılan natal + synastry tightness kaynağı.

Amaç: Tek canlı orb policy source-of-truth. `promise_vector_engine.py` ve
`synastry_signature_router.py` tightness hesabını buradan alır.

### Curve şekli

Mevcut: lineer. `1.0 - orb / max_orb`, clamp [0, 1].

`CURVE_TYPE = "linear"` marker explicit. Cosine eğri önerisi (audit D2)
gelecekte AYRI bir PR'da alınacak — bu dosyaya tek config switch eklenerek
değiştirilebilecek şekilde ayrıldı.

### Zero-orb semantik divergence

Natal ve synastry **orb=0** davranışı farklı:

* Natal (default, `zero_orb_as_missing=False`):
    0° = en sıkı aspect → tightness = 1.0
* Synastry (`zero_orb_as_missing=True`):
    orb<=0 "missing data" sentinel → tightness = 0.0

Divergence kasıtlı mı bug mu ayrı bir soru (synastry hit'lerinde
`orb_deg` bazen 0 gelebiliyor — sentinel tasarım kararı gibi duruyor).
PR 2 bu kararı vermez, mevcut davranışı korur.

TODO(faz1-pr4): Synastry zero-orb semantiği audit edilmeli — gerçekten
'orb_deg=0' missing mi, yoksa data kaynağında pozitif bir tolerance
eklenip default `zero_orb_as_missing=False`'a geçilmeli mi?
"""
from __future__ import annotations

from typing import Mapping


# ----------------------------------------------------------------------------
# Orb tablosu — major aspect'ler için max allowed orb (derece).
# Bilinmeyen aspect'ler için FALLBACK_MAX_ORB kullanılır.
# ----------------------------------------------------------------------------

MAX_ORB_BY_ASPECT: Mapping[str, float] = {
    "conjunction": 8.0,
    "opposition": 8.0,
    "square": 7.0,
    "trine": 7.0,
    "sextile": 5.0,
}

FALLBACK_MAX_ORB: float = 6.0

CURVE_TYPE: str = "linear"


def max_orb_for(aspect: str) -> float:
    """Verilen aspect için max allowed orb. Bilinmeyen aspect → FALLBACK."""
    return MAX_ORB_BY_ASPECT.get(aspect.lower(), FALLBACK_MAX_ORB)


def tightness(
    aspect: str,
    orb: float,
    *,
    zero_orb_as_missing: bool = False,
) -> float:
    """Aspect tightness 0..1 aralığında.

    Args:
        aspect: Aspect adı (conjunction, square, trine...). Case-insensitive.
        orb: Orb derece.
        zero_orb_as_missing: True → orb<=0 missing data sentinel, tightness=0.
            False (default, natal konvansiyonu) → orb=0 max tightness (=1).

    Returns:
        Lineer tightness değeri `[0, 1]` aralığında.

    Notes:
        Non-numeric orb → 0.0. Negatif orb (zero_orb_as_missing=False
        durumunda) asla 1.0'ı geçmez; pozitif yönde ise max_orb ötesinde
        clamp 0.0.
    """
    try:
        orb_f = float(orb)
    except (TypeError, ValueError):
        return 0.0

    if zero_orb_as_missing and orb_f <= 0.0:
        return 0.0

    max_orb = max_orb_for(aspect)
    if max_orb <= 0.0:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (orb_f / max_orb)))
