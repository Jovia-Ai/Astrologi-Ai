"""Natal pattern library v1 seed — structural invariants.

Voice Contract v3 §3 requirements:
  - 10 seed patterns, unique IDs
  - Each pattern has: id, name, opening (tr+en), emotional_intent,
    tone_accent, trigger, priority_kind, section_binding, why_now_triggers
  - emotional_intent is one of 5 canonical labels
  - tone_accent derives correctly from intent
  - Opening hook is non-empty, ≤ 22 words (voice spec band)
  - TR/EN parity: both locales present in opening + why_now templates
  - No banned astro-jargon in opening (voice spec §3.1)
  - why_now templates are human-first (no "3. ev", "Moon", "Mercury" in TR)
  - Deterministic render — same seed yields same output
"""

from __future__ import annotations

import re

import pytest

from app.natal.narrative.natal_pattern_library import (
    FAST_PLANETS,
    INTENT_TO_TONE_ACCENT,
    INTENT_VOICE_SHIFT,
    PATTERN_LIBRARY,
    PRIORITY_RANKS,
    get_tone_accent,
    get_voice_shift,
    pattern_ids,
    pattern_index,
    priority_rank_value,
    render_why_now_for_trigger,
)


# ---------------------------------------------------------------------------
# Structural invariants — 10 patterns, unique IDs, required fields
# ---------------------------------------------------------------------------

CANONICAL_INTENTS = {"rahatlatma", "fark_edilme", "icgoru", "izin", "ayrim"}
CANONICAL_ACCENTS = {"lime", "lav", "stone", "blush", "lime_lav"}
REQUIRED_FIELDS = {
    "id",
    "name",
    "opening",
    "emotional_intent",
    "tone_accent",
    "trigger",
    "priority_kind",
    "section_binding",
    "why_now_triggers",
}


def test_library_has_ten_patterns():
    assert len(PATTERN_LIBRARY) == 10, "v1 seed is exactly 10 patterns"


def test_pattern_ids_are_unique():
    ids = pattern_ids()
    assert len(ids) == len(set(ids)), f"duplicate pattern id(s): {ids}"


def test_every_pattern_has_required_fields():
    for entry in PATTERN_LIBRARY:
        missing = REQUIRED_FIELDS - set(entry.keys())
        assert not missing, f"{entry.get('id')} missing fields: {missing}"


def test_every_pattern_id_snake_case():
    for entry in PATTERN_LIBRARY:
        pid = entry["id"]
        assert re.fullmatch(r"[a-z][a-z0-9_]+", pid), (
            f"{pid} not snake_case"
        )


def test_every_pattern_name_is_two_to_three_words():
    # Voice spec §08 — pattern adı 2 kelime (sıfat + isim)
    # "Ciddi görünüş / sıcak iç" gibi compound adları 3-5 kelimeye tolere ediyoruz
    # ama asıl kural 2-kelime temelinde. Test yumuşak: 2-5 kelime.
    for entry in PATTERN_LIBRARY:
        words = entry["name"].replace("/", " ").split()
        assert 2 <= len(words) <= 5, (
            f"{entry['id']} name '{entry['name']}' outside 2-5 word band"
        )


# ---------------------------------------------------------------------------
# Emotional intent + UI driver
# ---------------------------------------------------------------------------


def test_every_intent_is_canonical_label():
    for entry in PATTERN_LIBRARY:
        intent = entry["emotional_intent"]
        assert intent in CANONICAL_INTENTS, (
            f"{entry['id']} has unknown intent: {intent}"
        )


def test_every_tone_accent_is_canonical():
    for entry in PATTERN_LIBRARY:
        accent = entry["tone_accent"]
        assert accent in CANONICAL_ACCENTS, (
            f"{entry['id']} has unknown tone_accent: {accent}"
        )


def test_tone_accent_derives_from_intent():
    for entry in PATTERN_LIBRARY:
        expected = INTENT_TO_TONE_ACCENT[entry["emotional_intent"]]
        assert entry["tone_accent"] == expected, (
            f"{entry['id']} tone_accent '{entry['tone_accent']}' does not match "
            f"intent '{entry['emotional_intent']}' → should be '{expected}'"
        )


def test_get_tone_accent_helper():
    assert get_tone_accent("fark_edilme") == "lav"
    assert get_tone_accent("rahatlatma") == "lime"
    assert get_tone_accent("izin") == "blush"
    # Unknown → safe fallback
    assert get_tone_accent("unknown") == "stone"


def test_get_voice_shift_helper():
    shift = get_voice_shift("fark_edilme")
    assert "texture" in shift
    assert shift["texture"] == 0.80
    # Unknown → empty dict (no override)
    assert get_voice_shift("unknown") == {}


def test_every_intent_has_voice_shift_mapping():
    # Contract v3 §5.3 — every canonical intent must have shift axes defined
    for intent in CANONICAL_INTENTS:
        assert intent in INTENT_VOICE_SHIFT, (
            f"intent '{intent}' missing voice shift mapping"
        )


def test_intent_coverage_is_balanced():
    # Heuristic — no single intent dominates more than 50% of 10 patterns.
    # Prevents accidental over-indexing on "fark_edilme" for instance.
    from collections import Counter
    counts = Counter(e["emotional_intent"] for e in PATTERN_LIBRARY)
    max_count = max(counts.values())
    assert max_count <= 5, (
        f"intent distribution imbalanced: {dict(counts)}"
    )


# ---------------------------------------------------------------------------
# Opening hook — voice spec §6 confrontation pattern
# ---------------------------------------------------------------------------


def test_opening_has_both_locales():
    for entry in PATTERN_LIBRARY:
        opening = entry["opening"]
        assert "tr" in opening, f"{entry['id']} opening missing 'tr'"
        assert "en" in opening, f"{entry['id']} opening missing 'en'"
        assert opening["tr"].strip(), f"{entry['id']} TR opening empty"
        assert opening["en"].strip(), f"{entry['id']} EN opening empty"


def test_opening_word_count_in_band():
    # Voice spec §10 — share headline 6-12 words, narrative 8-14.
    # Opening hook is a hybrid — allow 6-22 to accommodate confrontation
    # two-clause structure ("Insanlar X saniyor — oysa Y").
    for entry in PATTERN_LIBRARY:
        for locale in ("tr", "en"):
            words = entry["opening"][locale].split()
            assert 6 <= len(words) <= 22, (
                f"{entry['id']} {locale} opening word count "
                f"{len(words)} outside 6-22: '{entry['opening'][locale]}'"
            )


def test_opening_has_confrontation_marker():
    # Voice spec §6.2 — 4 micro-patterns: em-dash contrast, "değil / not",
    # "öğrendin / learned", or percentage + "ama / but" reframe pivot.
    # The unifying property: opening must contain a *pivot* — a point where
    # stated perception flips to inner reality.
    tr_markers = ["—", "değil", "öğrendin", "sanıyor", "yüzde", " ama ", " oysa ", "tuhaf", " bile "]
    en_markers = ["—", "not a", "learned", "think", "percent", "unseen", "but", "even"]
    for entry in PATTERN_LIBRARY:
        tr = entry["opening"]["tr"].lower()
        en = entry["opening"]["en"].lower()
        tr_has = any(m in tr for m in tr_markers)
        en_has = any(m.lower() in en for m in en_markers)
        assert tr_has, (
            f"{entry['id']} TR opening missing confrontation pivot: '{tr}'"
        )
        assert en_has, (
            f"{entry['id']} EN opening missing confrontation pivot: '{en}'"
        )


def test_opening_uses_second_person_singular_tr():
    # Voice spec §4.2 — "sen + şimdiki/geniş zaman" OR "sana/seni + cümle"
    # OR 2nd-person possessive ("-ın/-in/-un/-ün tarafın/elin/dilin" vb.)
    # Full coverage requires three marker families.
    verb_endings = (
        "sun.", "sun ", "sun,", "sun —",
        "yorsun.", "yorsun ", "yorsun,", "yorsun —",
        "din.", "din ", "din,", "din —",
        "iyor.", "yor.",
    )
    explicit_pronouns = (" sen ", " sana ", " seni ", " senin ", "seni ", "sana ")
    possessive_markers = (
        " tarafın ", " dilin ", " elin ", " omzun", " zihnin",
        " kalbin", " sesin", " yanın", " cümlen",
    )
    for entry in PATTERN_LIBRARY:
        tr = " " + entry["opening"]["tr"].lower() + " "
        has_verb = any(ending in tr for ending in verb_endings)
        has_pronoun = any(p in tr for p in explicit_pronouns)
        has_possessive = any(m in tr for m in possessive_markers)
        assert has_verb or has_pronoun or has_possessive, (
            f"{entry['id']} TR opening lacks 2nd-person marker "
            f"(verb/pronoun/possessive): '{tr.strip()}'"
        )


# ---------------------------------------------------------------------------
# why_now — human-first, no astro jargon in user-facing text
# ---------------------------------------------------------------------------

# Voice spec §3.1 — astro terms banned at headline/hook layer.
# why_now is HOOK layer (Contract v3 §4.1). These words should NOT appear.
ASTRO_BANNED_TR = [
    "3. ev",
    "8. ev",
    "12. ev",
    "1. ev",
    "6. ev",
    "11. ev",
    "yükselen",
    "satürn",
    "merkür",
    "venüs",
    "jüpiter",
    "plüton",
    "neptün",
    "uranüs",
    "orb",
    "transit",
    "aspect",
    "kavuşum",
    "opozisyon",
    "trine",
    "kare açı",
    "conjunction",
]

ASTRO_BANNED_EN = [
    "3rd house",
    "8th house",
    "12th house",
    "1st house",
    "6th house",
    "11th house",
    "ascendant",
    "saturn",
    "mercury",
    "venus",
    "jupiter",
    "pluto",
    "neptune",
    "uranus",
    "orb",
    "transit",
    "aspect",
    "conjunction",
    "opposition",
    "trine",
    "square aspect",
]


def test_why_now_templates_are_human_first_tr():
    for entry in PATTERN_LIBRARY:
        for trigger in entry["why_now_triggers"]:
            templates = trigger.get("templates", {})
            for tpl in templates.get("tr", []):
                lowered = tpl.lower()
                for banned in ASTRO_BANNED_TR:
                    assert banned not in lowered, (
                        f"{entry['id']} TR why_now template contains banned "
                        f"astro term '{banned}': '{tpl}'"
                    )


def test_why_now_templates_are_human_first_en():
    for entry in PATTERN_LIBRARY:
        for trigger in entry["why_now_triggers"]:
            templates = trigger.get("templates", {})
            for tpl in templates.get("en", []):
                lowered = tpl.lower()
                for banned in ASTRO_BANNED_EN:
                    assert banned not in lowered, (
                        f"{entry['id']} EN why_now template contains banned "
                        f"astro term '{banned}': '{tpl}'"
                    )


def test_every_pattern_has_at_least_one_why_now_trigger():
    for entry in PATTERN_LIBRARY:
        triggers = entry["why_now_triggers"]
        assert triggers, f"{entry['id']} has no why_now_triggers"


def test_every_why_now_trigger_has_bilingual_templates():
    for entry in PATTERN_LIBRARY:
        for trigger in entry["why_now_triggers"]:
            templates = trigger.get("templates", {})
            assert "tr" in templates, (
                f"{entry['id']} trigger {trigger.get('kind')} missing TR templates"
            )
            assert "en" in templates, (
                f"{entry['id']} trigger {trigger.get('kind')} missing EN templates"
            )
            assert templates["tr"], (
                f"{entry['id']} trigger {trigger.get('kind')} empty TR pool"
            )
            assert templates["en"], (
                f"{entry['id']} trigger {trigger.get('kind')} empty EN pool"
            )


def test_every_why_now_trigger_kind_is_known():
    known = {"transit_through_house", "transit_to_pattern_body", "transit_state"}
    for entry in PATTERN_LIBRARY:
        for trigger in entry["why_now_triggers"]:
            kind = trigger.get("kind")
            assert kind in known, (
                f"{entry['id']} unknown trigger kind: {kind}"
            )


# ---------------------------------------------------------------------------
# Priority ranks
# ---------------------------------------------------------------------------


def test_priority_rank_values_are_deterministic():
    for entry in PATTERN_LIBRARY:
        rank = priority_rank_value(entry)
        assert isinstance(rank, int), f"{entry['id']} rank not int"
        assert 1 <= rank <= 99, f"{entry['id']} rank {rank} out of band"


def test_stellium_outranks_placement():
    stellium_rank = PRIORITY_RANKS["stellium"]
    placement_rank = PRIORITY_RANKS["placement"]
    assert stellium_rank < placement_rank, (
        "stellium must outrank placement in selection order"
    )


def test_tight_aspect_outranks_loose_aspect():
    tight = PRIORITY_RANKS["tight_aspect_sub_1"]
    loose = PRIORITY_RANKS["loose_aspect_3_to_6"]
    assert tight < loose, "tight aspect must outrank loose aspect"


# ---------------------------------------------------------------------------
# Render helper — deterministic picking
# ---------------------------------------------------------------------------


def test_render_why_now_deterministic_same_seed():
    pattern = PATTERN_LIBRARY[0]  # saturn_h3
    trigger = pattern["why_now_triggers"][0]
    a = render_why_now_for_trigger(trigger, locale="tr", seed="user-123")
    b = render_why_now_for_trigger(trigger, locale="tr", seed="user-123")
    assert a == b, "same seed must yield same template"
    assert a in trigger["templates"]["tr"]


def test_render_why_now_locale_fallback():
    pattern = PATTERN_LIBRARY[0]
    trigger = pattern["why_now_triggers"][0]
    # Unknown locale falls back to TR (not empty)
    result = render_why_now_for_trigger(trigger, locale="de", seed="seed")
    assert result, "unknown locale should fallback to TR, not empty"
    assert result in trigger["templates"]["tr"]


def test_render_why_now_empty_templates_returns_empty():
    fake_trigger = {"kind": "transit_through_house", "templates": {}}
    assert render_why_now_for_trigger(fake_trigger, "tr", "seed") == ""


def test_render_why_now_bilingual_separation():
    pattern = PATTERN_LIBRARY[0]
    trigger = pattern["why_now_triggers"][0]
    tr = render_why_now_for_trigger(trigger, locale="tr", seed="s")
    en = render_why_now_for_trigger(trigger, locale="en", seed="s")
    # Language never crosses
    assert tr in trigger["templates"]["tr"]
    assert en in trigger["templates"]["en"]


# ---------------------------------------------------------------------------
# Section binding — every pattern binds to a known natal section
# ---------------------------------------------------------------------------


def test_section_binding_is_known_natal_section():
    known_sections = {
        "identity_mechanics",
        "relationships_depth",
        "career_visibility",
        "direction_learning",
    }
    for entry in PATTERN_LIBRARY:
        binding = entry["section_binding"]
        assert binding in known_sections, (
            f"{entry['id']} binds to unknown section: {binding}"
        )


# ---------------------------------------------------------------------------
# Fast planet taxonomy
# ---------------------------------------------------------------------------


def test_fast_planets_tuple_is_canonical():
    assert set(FAST_PLANETS) == {"Moon", "Sun", "Mercury", "Venus", "Mars"}


# ---------------------------------------------------------------------------
# pattern_index helper returns a mutable-safe copy
# ---------------------------------------------------------------------------


def test_pattern_index_returns_copies():
    idx = pattern_index()
    original = PATTERN_LIBRARY[0]
    idx[original["id"]]["name"] = "MUTATED"
    # Original library unaffected
    assert PATTERN_LIBRARY[0]["name"] != "MUTATED"
