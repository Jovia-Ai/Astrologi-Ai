"""Essential dignity — Faz 2 PR 6.

Planet × sign essential dignity tabloları + konservatif weight'ler +
per-archetype dignity bonus hesabı.

### Opinionated kararlar (commit-level açık)

1. **Modern planet'ler (Uranus/Neptune/Pluto)** sadece domicile tanındı;
   exaltation/detriment/fall klasik tablolarda yok olduğu için peregrine
   kalır. Bu karar modern astrolojik gelenekleri (Uranus-Aquarius ortak
   yöneticiliği) kabul eder ama modern "karşı" kategorilere genişletmez.

2. **Triplicity, terms, faces** (ileri klasik minör dignity tabloları)
   dahil edilmedi — PR 6 scope'u *essential* dignity ile sınırlı.

3. **Peregrine** basitleştirilmiş tanım: not in {domicile, exaltation,
   detriment, fall}. Tam klasik peregrine (hiçbir minör dignity'ye sahip
   değil) gelecek PR'a bırakıldı.

4. **Additive, multiplicative DEĞİL.** Dignity weight sect ile compound
   edilmez. PR 7 sect geldiğinde formül: `base + dignity + sect` şeklinde
   strict additive. Bu dosyada `dignity_weight` döndüren function'lar
   saf sayısal değerler; caller'ın ek katmanlarla toplamaktan başka bir
   şey yapması beklenmez.

### Archetype signature planets

`ARCHETYPE_SIGNATURE_PLANETS` haritası opinionated bir archetype →
signature planet(ler) eşlemesi. Bu tabloya girmeyen arketipler
dignity_bonus=0 alır (graceful fallback). Yeni arketip eklenirse buraya
da eklenmeli — sessiz scoring asimetrisi önlenir.
"""
from __future__ import annotations

from typing import Literal, Mapping, Sequence


DignityKind = Literal["domicile", "exaltation", "detriment", "fall", "peregrine"]


# --- Astronomical facts (constants, not config) --------------------------

# Traditional + modern rulerships. Her planet 1 veya 2 sign'a sahip olabilir.
# Modern planetler klasik rulership tablosuna eklenmez; ayrıca co-ruler listesi
# olarak dahil edilir.
_TRADITIONAL_RULERSHIPS: Mapping[str, Sequence[str]] = {
    "sun": ("leo",),
    "moon": ("cancer",),
    "mercury": ("gemini", "virgo"),
    "venus": ("taurus", "libra"),
    "mars": ("aries", "scorpio"),
    "jupiter": ("sagittarius", "pisces"),
    "saturn": ("capricorn", "aquarius"),
}

_MODERN_RULERSHIPS: Mapping[str, Sequence[str]] = {
    "uranus": ("aquarius",),
    "neptune": ("pisces",),
    "pluto": ("scorpio",),
}

RULERSHIPS: Mapping[str, Sequence[str]] = {
    **_TRADITIONAL_RULERSHIPS,
    **_MODERN_RULERSHIPS,
}

# Exaltation — sadece traditional 7 planet. Modern planetler peregrine.
EXALTATIONS: Mapping[str, str] = {
    "sun": "aries",
    "moon": "taurus",
    "mercury": "virgo",
    "venus": "pisces",
    "mars": "capricorn",
    "jupiter": "cancer",
    "saturn": "libra",
}

# Zodiac opposite map — detriment ve fall derivasyonu için.
_OPPOSITE_SIGN: Mapping[str, str] = {
    "aries": "libra",
    "libra": "aries",
    "taurus": "scorpio",
    "scorpio": "taurus",
    "gemini": "sagittarius",
    "sagittarius": "gemini",
    "cancer": "capricorn",
    "capricorn": "cancer",
    "leo": "aquarius",
    "aquarius": "leo",
    "virgo": "pisces",
    "pisces": "virgo",
}


# --- Weight policy -------------------------------------------------------

# Konservatif başlangıç değerleri (PR 6 user-onaylı).
# Telemetri sonrası ayarlanabilir; `scoring_profile_version` bump yalnız
# user-facing yeni generation'da.
DIGNITY_WEIGHTS: Mapping[DignityKind, float] = {
    "domicile": 0.15,
    "exaltation": 0.10,
    "peregrine": 0.0,
    "detriment": -0.10,
    "fall": -0.15,
}


# --- Archetype → signature planet(s) mapping -----------------------------

# Opinionated mapping. Taxonomy'deki archetype'lerin dominant planet
# karakterini yansıtır. Yeni archetype eklenirse buraya eklenmeli.
# Kayıtlı olmayan archetype ID → boş tuple → dignity_bonus = 0 (graceful).
ARCHETYPE_SIGNATURE_PLANETS: Mapping[str, Sequence[str]] = {
    "builder": ("saturn",),
    "visionary": ("jupiter",),
    "analyst": ("mercury",),
    "connector": ("venus",),
    "guardian": ("saturn", "moon"),
    "depthkeeper": ("pluto", "mars"),
    "catalyst": ("uranus", "mars"),
}


# --- Lookup functions ----------------------------------------------------


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def essential_dignity(planet: str | None, sign: str | None) -> DignityKind:
    """Planet × sign → essential dignity kategorisi.

    Algoritma sırası (precedence):
      1. domicile (rulership) — öncelik en yüksek. Mercury@Virgo gibi
         hem ruler hem exaltation olan case'lerde domicile kazanır.
      2. exaltation
      3. detriment — rulership sign'ının zıttı
      4. fall — exaltation sign'ının zıttı
      5. peregrine — bunların hiçbiri değil

    Bilinmeyen/boş planet/sign → peregrine (fallback).
    """
    planet_key = _normalize(planet)
    sign_key = _normalize(sign)
    if not planet_key or not sign_key:
        return "peregrine"

    if sign_key in RULERSHIPS.get(planet_key, ()):
        return "domicile"
    if EXALTATIONS.get(planet_key) == sign_key:
        return "exaltation"
    # Detriment yalnız TRADITIONAL rulership'ten derive edilir. Modern
    # planetlerin (Uranus/Neptune/Pluto) detriment'i opinionated olarak
    # tanınmıyor — scope docstring'inde açıkça belirtildi.
    detriment_signs = {
        _OPPOSITE_SIGN[s]
        for s in _TRADITIONAL_RULERSHIPS.get(planet_key, ())
        if s in _OPPOSITE_SIGN
    }
    if sign_key in detriment_signs:
        return "detriment"
    exalt_sign = EXALTATIONS.get(planet_key)
    if exalt_sign and _OPPOSITE_SIGN.get(exalt_sign) == sign_key:
        return "fall"
    return "peregrine"


def dignity_weight(planet: str | None, sign: str | None) -> float:
    """Essential dignity kategorisi → konservatif weight.

    Peregrine → 0.0 (zero-diff fallback için güvenli).
    Bilinmeyen planet/sign → peregrine → 0.0.
    """
    return DIGNITY_WEIGHTS[essential_dignity(planet, sign)]


def archetype_dignity_bonus(
    archetype_id: str | None,
    planet_signs: Mapping[str, str],
) -> float:
    """Bir arketip için toplam dignity bonus.

    `planet_signs`: {planet_name: sign_name} — chart'taki gezegenlerin
    bulunduğu sign'lar. Arketipin `ARCHETYPE_SIGNATURE_PLANETS` tablosundaki
    signature planet(ler)inin dignity weight'leri toplanır.

    Bilinmeyen arketip → 0.0 (graceful fallback).
    Planet chart'ta yoksa o signature planet için 0.0 (peregrine).

    Returns:
        Toplam bonus (işaretli float). Tipik aralık [-0.30, +0.30] —
        çift signature arketiplerde iki fall kadar kötü, iki domicile kadar
        iyi. Tek signature arketiplerde [-0.15, +0.15].
    """
    archetype_key = _normalize(archetype_id)
    if not archetype_key:
        return 0.0
    signature = ARCHETYPE_SIGNATURE_PLANETS.get(archetype_key, ())
    if not signature:
        return 0.0
    total = 0.0
    for planet in signature:
        sign = _normalize(planet_signs.get(planet.capitalize()) or planet_signs.get(planet))
        total += dignity_weight(planet, sign)
    return total
