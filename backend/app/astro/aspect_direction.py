"""Aspect direction (applying / separating / exact) — Faz 2 PR 5.

Swiss Ephemeris signed speed'leri kullanarak iki body arasındaki aspect'in
yön durumunu hesaplar.

### Kanonik rule

Mevcut signed separation `sep = L_A - L_B` (mod 360, [-180..180] aralığında).
Aspect'in hedef açısı θ (conjunction=0, sextile=60, square=90, trine=120,
opposition=180). Aspect iki yönde de ortaya çıkabilir (ör. square ±90).

1. `signed_dev = signed_angle(sep - θ)` ya da `signed_angle(sep + θ)` —
   hangi |dev| küçükse o taraf (closer side of exact aspect)
2. `current_orb = |signed_dev|`
3. `|current_orb| < EXACT_ORB_EPSILON` → **"exact"**
4. Speed verisi eksikse → **None** (wrapper'da multiplier=1.0 fallback)
5. `|relative_speed| < SPEED_EPSILON` → **None** (stasyoner / eş hız,
   yön belirsiz — geniş orb yanlışlıkla "exact" etiketlenmesin)
6. `d(orb)/dt = sign(signed_dev) * relative_speed`
   - `< 0` → orb shrinking → **"applying"**
   - `> 0` → orb growing → **"separating"**

Analitik derivative yaklaşımı kullanılır (dt-bağımsız). Projection-based
yaklaşım (1-day forward) fast-moving bodies için (Moon ~12.5°/gün) dar
orb aspect'lerini atlıyor ve yanlış direction üretiyordu.

### Retrograde davranışı — geometric rule first

Swiss Ephemeris retrograde body'lere negatif speed verir. Relative speed
hesabı bu sign'ı doğal handle eder. Klasik "retrograde body truly apply
edemez" görüşü **PR 5'te uygulanmıyor** — direction tamamen geometrik.
Bu opinionated karar; ileride config switch olarak eklenebilir.

### Fail-safe

Bilinmeyen aspect adı, eksik speed, stasyoner edge case → hepsi `None`
döner. `None` upstream'de multiplier=1.0'a mapleniyor → zero-diff
fallback. Production'da hiçbir edge case'de hata fırlatmaz.
"""
from __future__ import annotations

from typing import Literal, Mapping, Optional


# Astrolojik olarak "really exact" — ne çok dar (matematiksel 0) ne çok geniş.
# ~6 arc-minute; stationing edge cases'i yakalar.
EXACT_ORB_EPSILON: float = 0.1

# Stasyoner / eş hız eşiği (derece/gün). Bu eşiğin altında yön belirsiz.
SPEED_EPSILON: float = 0.01

# Major aspect hedef açıları (derece). Bilinmeyen aspect → None direction.
ASPECT_ANGLES: Mapping[str, float] = {
    "conjunction": 0.0,
    "sextile": 60.0,
    "square": 90.0,
    "trine": 120.0,
    "opposition": 180.0,
}

Direction = Literal["applying", "separating", "exact"]


def _signed_angle(x: float) -> float:
    """Açıyı `[-180, 180]` aralığına normalize et."""
    return ((x + 180.0) % 360.0) - 180.0


def _closer_signed_deviation(sep: float, target: float) -> float:
    """Aspect iki yönde de var olabilir (ör. square ±90). Daha yakın olan
    taraftan işaretli sapma döner — `signed_angle(sep ± target)`.
    """
    dev_plus = _signed_angle(sep - target)
    dev_minus = _signed_angle(sep + target)
    if abs(dev_plus) <= abs(dev_minus):
        return dev_plus
    return dev_minus


def compute_direction(
    aspect_name: str,
    a_longitude: float | None,
    b_longitude: float | None,
    a_speed: float | None,
    b_speed: float | None,
) -> Optional[Direction]:
    """Aspect direction for the two-body configuration.

    Args:
        aspect_name: aspect adı (case-insensitive). Major aspect'ler dışı → None.
        a_longitude, b_longitude: body longitudes (derece, 0..360).
        a_speed, b_speed: signed angular velocities (derece/gün). Swiss
            Ephemeris negatif değer = retrograde. None → yön hesaplanamaz.

    Returns:
        `"applying"`, `"separating"`, `"exact"`, veya None (indeterminate).

    Implementation note:
        Analitik derivative (dt-bağımsız). `d(orb)/dt = sign(signed_dev) *
        rel_speed`. Negative → applying, positive → separating. Projection
        yaklaşımı (1-day forward) fast-moving bodies (Moon) için exact'i
        atlıyor ve yanlış direction üretiyordu.
    """
    target = ASPECT_ANGLES.get(aspect_name.lower()) if aspect_name else None
    if target is None:
        return None
    if a_longitude is None or b_longitude is None:
        return None

    try:
        lon_a = float(a_longitude)
        lon_b = float(b_longitude)
    except (TypeError, ValueError):
        return None

    sep = _signed_angle(lon_a - lon_b)
    signed_dev = _closer_signed_deviation(sep, target)
    current_orb = abs(signed_dev)

    if current_orb < EXACT_ORB_EPSILON:
        return "exact"

    if a_speed is None or b_speed is None:
        return None

    try:
        rel_speed = float(a_speed) - float(b_speed)
    except (TypeError, ValueError):
        return None

    if abs(rel_speed) < SPEED_EPSILON:
        # Stasyoner / eşdeğer hız. Yön belirsiz; "exact" etiketlemekten
        # kaçın (orb hâlâ geniş olabilir). Fallback None.
        return None

    # d(orb)/dt = sign(signed_dev) * rel_speed
    derivative = (1.0 if signed_dev > 0 else -1.0) * rel_speed

    if derivative < 0:
        return "applying"
    return "separating"


# Direction → tightness multiplier (natal wrapper'da uygulanır, orb_policy
# tarafında yok). Konservatif başlangıç: applying/exact %10 bonus, separating
# penaltısız. Telemetri sonrası ayarlanabilir.
DIRECTION_TIGHTNESS_BONUS: Mapping[str, float] = {
    "applying": 1.10,
    "exact": 1.10,
    "separating": 1.00,
}


def direction_multiplier(direction: Optional[str]) -> float:
    """Direction label → tightness multiplier. Bilinmeyen / None → 1.0."""
    if direction is None:
        return 1.0
    return DIRECTION_TIGHTNESS_BONUS.get(direction, 1.0)
