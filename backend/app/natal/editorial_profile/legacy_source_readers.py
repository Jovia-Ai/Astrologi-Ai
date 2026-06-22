"""Narrowly scoped, read-only readers for R2-audited legacy source families.

Each reader accesses a legacy constant/library directly (no builder/selection
execution), enumerates its placement keys, and normalizes one entry's fields
verbatim into a ResolvedContent. Field names are normalized; content text is
preserved byte-for-byte.

Supported source families (R2-audited, registry-backed):
  - PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1   (contracts.py)
  - PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1    (contracts.py)
  - PERSONALITY_IMPRINT_LIBRARY_TR_V3.<moon|mercury|venus|mars>_signs  (sign_support_library.py)
  - PERSONALITY_IMPRINT_LIBRARY_TR_V4.<sun|jupiter|saturn>_signs       (tone_support_library.py)
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Callable, Dict, Tuple

from .legacy_asset_contracts import ResolvedContent

# ── lazy library access (constants only) ─────────────────────────────────────
# Imported lazily so the package stays dormant unless a reader is actually used.


def _contracts():
    from app.natal.personality_imprint import contracts as _c
    return _c


def _sign_library() -> dict:
    from app.natal.personality_imprint import sign_support_library as _s
    return _s.PERSONALITY_IMPRINT_LIBRARY_TR_V3


def _tone_library() -> dict:
    from app.natal.personality_imprint import tone_support_library as _t
    return _t.PERSONALITY_IMPRINT_LIBRARY_TR_V4


# ── source family descriptors ────────────────────────────────────────────────
@dataclass(frozen=True)
class SourceFamily:
    family_id: str          # logical id used by readers
    source_path: str        # repo-relative path
    source_symbol: str      # legacy symbol / family
    entries: Callable[[], Tuple[dict, ...]]  # returns the raw list (verbatim)


def _list_entries(loader: Callable[[], list]) -> Callable[[], Tuple[dict, ...]]:
    def _inner() -> Tuple[dict, ...]:
        return tuple(loader())
    return _inner


SOURCE_FAMILIES: Dict[str, SourceFamily] = {
    "PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1",
        source_path="backend/app/natal/personality_imprint/contracts.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1",
        entries=_list_entries(lambda: _contracts().PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1",
        source_path="backend/app/natal/personality_imprint/contracts.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1",
        entries=_list_entries(lambda: _contracts().PERSONALITY_IMPRINT_LIBRARY_TR_SUPPORT_HOUSES_V1),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V3.moon_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V3.moon_signs",
        source_path="backend/app/natal/personality_imprint/sign_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V3.moon_signs",
        entries=_list_entries(lambda: _sign_library()["moon_signs"]),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V3.mercury_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V3.mercury_signs",
        source_path="backend/app/natal/personality_imprint/sign_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V3.mercury_signs",
        entries=_list_entries(lambda: _sign_library()["mercury_signs"]),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V3.venus_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V3.venus_signs",
        source_path="backend/app/natal/personality_imprint/sign_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V3.venus_signs",
        entries=_list_entries(lambda: _sign_library()["venus_signs"]),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V3.mars_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V3.mars_signs",
        source_path="backend/app/natal/personality_imprint/sign_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V3.mars_signs",
        entries=_list_entries(lambda: _sign_library()["mars_signs"]),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V4.sun_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V4.sun_signs",
        source_path="backend/app/natal/personality_imprint/tone_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V4.sun_signs",
        entries=_list_entries(lambda: _tone_library()["sun_signs"]),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V4.jupiter_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V4.jupiter_signs",
        source_path="backend/app/natal/personality_imprint/tone_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V4.jupiter_signs",
        entries=_list_entries(lambda: _tone_library()["jupiter_signs"]),
    ),
    "PERSONALITY_IMPRINT_LIBRARY_TR_V4.saturn_signs": SourceFamily(
        family_id="PERSONALITY_IMPRINT_LIBRARY_TR_V4.saturn_signs",
        source_path="backend/app/natal/personality_imprint/tone_support_library.py",
        source_symbol="PERSONALITY_IMPRINT_LIBRARY_TR_V4.saturn_signs",
        entries=_list_entries(lambda: _tone_library()["saturn_signs"]),
    ),
}

# Registry symbol_or_family -> reader family_id. Aliases resolve logical R2
# family names onto the concrete legacy symbol they describe (documented in the
# R3B report). No content is borrowed across families.
REGISTRY_FAMILY_ALIASES: Dict[str, str] = {
    # asset #1 logical combined name -> priority houses (representative house bank)
    "PERSONALITY_IMPRINT_LIBRARY_TR_V1": "PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1",
    # asset #2 logical priority alias -> priority houses
    "PERSONALITY_IMPRINT_LIBRARY_TR_V2": "PERSONALITY_IMPRINT_LIBRARY_TR_PRIORITY_HOUSES_V1",
}


def reader_family_id_for_registry_symbol(symbol: str) -> str | None:
    if symbol in SOURCE_FAMILIES:
        return symbol
    return REGISTRY_FAMILY_ALIASES.get(symbol)


def iter_entry_keys(family_id: str) -> Tuple[str, ...]:
    fam = SOURCE_FAMILIES[family_id]
    return tuple(str(e["key"]) for e in fam.entries() if isinstance(e, dict) and "key" in e)


def read_raw_entry(family_id: str, key: str) -> dict | None:
    fam = SOURCE_FAMILIES[family_id]
    for entry in fam.entries():
        if isinstance(entry, dict) and entry.get("key") == key:
            return entry
    return None


def family_content_hash(family_id: str) -> str:
    """Deterministic SHA-256 over the family's verbatim entries."""
    fam = SOURCE_FAMILIES[family_id]
    payload = json.dumps(
        [dict(e) for e in fam.entries()], ensure_ascii=False, sort_keys=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _clean(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_entry(raw: dict) -> ResolvedContent:
    """Normalize legacy field names; preserve content text verbatim.

    title <- label_tr ; summary <- aura ; body <- drive ; trait/shadow verbatim;
    gift/background_hint optional (house entries only).
    """
    return ResolvedContent(
        title=str(raw.get("label_tr", "")).strip(),
        summary=str(raw.get("aura", "")).strip(),
        body=str(raw.get("drive", "")).strip(),
        trait=_clean(raw.get("trait")),
        shadow=_clean(raw.get("shadow")),
        gift=_clean(raw.get("gift")),
        background_hint=_clean(raw.get("background_hint")),
    )


def content_is_complete(content: ResolvedContent) -> bool:
    return bool(content.title and content.summary and content.body)
