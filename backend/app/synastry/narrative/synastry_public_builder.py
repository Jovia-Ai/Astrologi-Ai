from __future__ import annotations

from typing import Any, Mapping, Sequence


def _round_score(value: Any) -> float:
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return 0.0


_HARD_CONSONANTS = set("fstkcpşhçFSTKCPŞHÇ")
_BACK_VOWELS = set("aıouAIOU")
_FRONT_VOWELS = set("eiöüEİÖÜ")


def _normalize_name(value: Any, fallback: str) -> str:
    text = str(value or "").strip()
    return text or fallback


def _last_vowel(text: str) -> str:
    for char in reversed(text):
        if char in _BACK_VOWELS or char in _FRONT_VOWELS:
            return char
    return "a"


def _ends_with_vowel(text: str) -> bool:
    if not text:
        return False
    char = text[-1]
    return char in _BACK_VOWELS or char in _FRONT_VOWELS


def _genitive_suffix(text: str) -> str:
    vowel = _last_vowel(text)
    if vowel in {"a", "ı", "A", "I"}:
        return "nın" if _ends_with_vowel(text) else "ın"
    if vowel in {"o", "u", "O", "U"}:
        return "nun" if _ends_with_vowel(text) else "un"
    if vowel in {"ö", "ü", "Ö", "Ü"}:
        return "nün" if _ends_with_vowel(text) else "ün"
    return "nin" if _ends_with_vowel(text) else "in"


def _dative_suffix(text: str) -> str:
    vowel = _last_vowel(text)
    base = "a" if vowel in _BACK_VOWELS else "e"
    return f"y{base}" if _ends_with_vowel(text) else base


def _locative_suffix(text: str) -> str:
    vowel = _last_vowel(text)
    base = "a" if vowel in _BACK_VOWELS else "e"
    last_char = text[-1] if text else ""
    prefix = "t" if last_char in _HARD_CONSONANTS else "d"
    return f"{prefix}{base}"


def _with_suffix(text: str, suffix: str) -> str:
    return f"{text}'{suffix}"


def _personalize_text(value: str, *, a_name: str, b_name: str) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    replacements = [
        ("A, B'de", f"{a_name}, {_with_suffix(b_name, _locative_suffix(b_name))}"),
        ("B, A'da", f"{b_name}, {_with_suffix(a_name, _locative_suffix(a_name))}"),
        ("A'nın", _with_suffix(a_name, _genitive_suffix(a_name))),
        ("A'nin", _with_suffix(a_name, _genitive_suffix(a_name))),
        ("B'nin", _with_suffix(b_name, _genitive_suffix(b_name))),
        ("B'nın", _with_suffix(b_name, _genitive_suffix(b_name))),
        ("A'ya", _with_suffix(a_name, _dative_suffix(a_name))),
        ("B'ye", _with_suffix(b_name, _dative_suffix(b_name))),
        ("A'da", _with_suffix(a_name, _locative_suffix(a_name))),
        ("B'de", _with_suffix(b_name, _locative_suffix(b_name))),
        ("A, B'da", f"{a_name}, {_with_suffix(b_name, _locative_suffix(b_name))}"),
        ("B, A'de", f"{b_name}, {_with_suffix(a_name, _locative_suffix(a_name))}"),
    ]
    for source, target in replacements:
        text = text.replace(source, target)
    return text


def _materialize_signature_entries(
    items: Sequence[Mapping[str, Any]],
    *,
    a_name: str,
    b_name: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        out.append(
            {
                "id": str(item.get("id") or ""),
                "category": str(item.get("category") or ""),
                "label": _personalize_text(str(item.get("label") or "").strip(), a_name=a_name, b_name=b_name),
                "one_liner": _personalize_text(str(item.get("one_liner") or "").strip(), a_name=a_name, b_name=b_name),
                "score": _round_score(item.get("score")),
                "astro_hint_soft": str(item.get("astro_hint_soft") or "").strip(),
            }
        )
    return [item for item in out if item["id"] and item["label"] and item["one_liner"]]


def _materialize_text_entries(
    items: Sequence[Mapping[str, Any]],
    *,
    a_name: str,
    b_name: str,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        out.append(
            {
                "id": str(item.get("id") or ""),
                "text": _personalize_text(str(item.get("text") or "").strip(), a_name=a_name, b_name=b_name),
                "score": _round_score(item.get("score")),
            }
        )
    return [item for item in out if item["id"] and item["text"]]


def build_synastry_imprint_public(
    selection: Mapping[str, Any],
    *,
    partner_a_name: str,
    partner_b_name: str,
) -> dict[str, Any] | None:
    if not isinstance(selection, Mapping):
        return None
    a_name = _normalize_name(partner_a_name, "Partner A")
    b_name = _normalize_name(partner_b_name, "Partner B")
    pair_signature = _materialize_signature_entries(selection.get("pair_signature") or [], a_name=a_name, b_name=b_name)
    a_to_b = _materialize_signature_entries(selection.get("a_to_b") or [], a_name=a_name, b_name=b_name)
    b_to_a = _materialize_signature_entries(selection.get("b_to_a") or [], a_name=a_name, b_name=b_name)
    together_field = _materialize_signature_entries(selection.get("together_field") or [], a_name=a_name, b_name=b_name)
    sweet_spots = _materialize_text_entries(selection.get("sweet_spots") or [], a_name=a_name, b_name=b_name)
    friction_points = _materialize_text_entries(selection.get("friction_points") or [], a_name=a_name, b_name=b_name)
    if not pair_signature and not a_to_b and not b_to_a and not together_field:
        return None
    return {
        "version": "synastry_imprint_v1",
        "headline": "İkinizin Arasında",
        "pair_signature": pair_signature,
        "a_to_b": a_to_b,
        "b_to_a": b_to_a,
        "together_field": together_field,
        "sweet_spots": sweet_spots,
        "friction_points": friction_points,
    }
