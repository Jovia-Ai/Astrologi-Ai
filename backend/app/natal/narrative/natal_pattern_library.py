"""Natal pattern library — v1 seed (10 patterns).

Voice Contract v3 §3 — minimum viable pattern system.
Each pattern = a thread's name + opening hook + emotional intent + why_now triggers.

Architecture principles (v3):
  - No scoring floats — int enum priority only
  - No public transit_ref — internal _debug only
  - 2-3 trigger types max (no activation_level)
  - Human-first why_now (no astro-first language)
  - First match wins — no tie-break scoring

References:
  - docs/voice/SHOU_BACKEND_UX_CONTRACT_v3.md (spec)
  - docs/voice/voice_spec.md §5 (layer taxonomy)
  - app/synastry/narrative/synastry_phrase_bank_tr.py (pattern engine template)
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Mapping, Tuple

# ---------------------------------------------------------------------------
# Type aliases — kept as plain dicts for JSON serialization compatibility.
# ---------------------------------------------------------------------------

EmotionalIntent = Literal[
    "rahatlatma",   # "not your fault" — trauma-informed softening
    "fark_edilme",  # "I see you" — surfacing an inner truth
    "icgoru",       # "I hadn't thought of it this way" — new angle (ASCII-safe key)
    "izin",         # "you're allowed" — dissolving guilt
    "ayrim",        # "X not Y" — reframe / paradox (ASCII-safe key)
]

ToneAccent = Literal["lime", "lav", "stone", "blush", "lime_lav"]

TriggerKind = Literal[
    "transit_through_house",   # fast planet in pattern's house
    "transit_to_pattern_body", # fast planet aspects pattern's main planet
    "transit_state",            # retrograde, station, sign ingress
]

PriorityKind = Literal[
    "tight_aspect_sub_1",    # orb < 1° aspect
    "stellium",               # 3+ planets same house
    "angular",                # house 1/4/7/10
    "tight_aspect_1_to_3",    # orb 1°-3°
    "placement",              # standard placement
    "loose_aspect_3_to_6",    # orb 3°-6°
]

FAST_PLANETS: Tuple[str, ...] = ("Moon", "Sun", "Mercury", "Venus", "Mars")


# ---------------------------------------------------------------------------
# Intent → UI driver mapping (Contract v3 §5.2)
# ---------------------------------------------------------------------------

INTENT_TO_TONE_ACCENT: Dict[str, ToneAccent] = {
    "rahatlatma":   "lime",
    "fark_edilme":  "lav",
    "icgoru":       "stone",
    "izin":         "blush",
    "ayrim":        "lime_lav",
}

# voice_profile_v2 axis overrides per intent (Contract v3 §5.3)
# Only applied to this thread's render — does NOT mutate profile-wide tone.
INTENT_VOICE_SHIFT: Dict[str, Dict[str, float]] = {
    "rahatlatma":   {"softening_level": 0.70, "warmth": 0.75},
    "fark_edilme":  {"texture": 0.80, "directness": 0.72},
    "icgoru":       {"holding_style": 0.70},
    "izin":         {"warmth": 0.80, "softening_level": 0.65},
    "ayrim":        {"directness": 0.90, "playfulness": 0.55},
}


# ---------------------------------------------------------------------------
# Priority rank — int enum, deterministic sort key. No floats.
# Lower value = higher priority. (Contract v3 §3.3)
# ---------------------------------------------------------------------------

PRIORITY_RANKS: Dict[PriorityKind, int] = {
    "tight_aspect_sub_1":   1,
    "stellium":             2,
    "angular":              3,
    "tight_aspect_1_to_3":  4,
    "placement":            5,
    "loose_aspect_3_to_6":  6,
}


# ---------------------------------------------------------------------------
# PATTERN LIBRARY — v1 seed (10 patterns)
# ---------------------------------------------------------------------------
# Each entry's shape is a plain dict so this module can be imported without
# any dataclass framework and pattern data can be JSON-serialized for debug.
#
# Opening hooks (Contract v3 §6) follow the 4 micro-patterns:
#   - "İnsanlar X sanıyor — oysa Y" (perception ≠ inner truth)
#   - "Bu bir X değil, Y" (rationalization reframe)
#   - "X öğrendin; şimdi Y tuhaf" (temporal pattern)
#   - "Yüzde N — ve sen buna X yapıyorsun" (number + complicity)
#
# why_now templates are HUMAN-FIRST (Contract v3 §4.1):
# User feeling comes first; astro reference lives in proof_raw/slide-ref.
# ---------------------------------------------------------------------------

PATTERN_LIBRARY: List[Dict[str, Any]] = [
    {
        "id": "saturn_h3_quiet_assessment",
        "name": "Sessiz değerlendirme",
        "opening": {
            "tr": "İnsanlar seni yavaş sanıyor — oysa her kelimeyi iki kez tartıyorsun.",
            "en": "People think you're slow — but you weigh every word twice.",
        },
        "emotional_intent": "fark_edilme",
        "tone_accent": "lav",
        "trigger": {"kind": "placement", "planet": "Saturn", "house": 3},
        "priority_kind": "placement",
        "section_binding": "identity_mechanics",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 3,
                "planet_filter": "fast",
                "templates": {
                    "tr": [
                        "Bugün söyleyeceğin her cümleyi içinden bir kez daha geçiriyorsun. Normalde de öyle — ama bugün daha sık.",
                        "Bugün ağzından çıkmadan önce her cümle içinde bir kere prova oluyor.",
                    ],
                    "en": [
                        "Today every sentence runs through you one more time before it leaves. You do this anyway — just more today.",
                        "Every sentence rehearses itself inside before it leaves your mouth today.",
                    ],
                },
            },
        ],
    },
    {
        "id": "moon_sq_mercury_intellectual_defense",
        "name": "Entelektüel savunma",
        "opening": {
            "tr": "Hissettiğini anlamadan söylemiyorsun. Seni koruyor, ama hissetmenden de alıyor.",
            "en": "You don't say what you feel until you've understood it. It protects you, but takes from the feeling too.",
        },
        "emotional_intent": "ayrim",
        "tone_accent": "lime_lav",
        "trigger": {
            "kind": "aspect",
            "planet_a": "Moon",
            "planet_b": "Mercury",
            "aspect": "square",
            "orb_max": 4.0,
        },
        "priority_kind": "tight_aspect_1_to_3",
        "section_binding": "identity_mechanics",
        "why_now_triggers": [
            {
                "kind": "transit_state",
                "state": "mercury_retrograde",
                "templates": {
                    "tr": [
                        "Bu hafta bir şey hissetmene fırsat kalmadan zihnin 'dur, bir bakayım' diyor.",
                        "Bu hafta duyguyu yakalamadan üstüne bir açıklama geçiriyorsun.",
                    ],
                    "en": [
                        "This week, before you can even feel something, your mind says \"hold on, let me check.\"",
                        "This week you put an explanation over a feeling before you've even caught it.",
                    ],
                },
            },
        ],
    },
    {
        "id": "mercury_cnj_venus_aesthetic_intelligence",
        "name": "Titiz estetik zeka",
        "opening": {
            "tr": "Güzel olmayan bir cümleyi ağzına alamıyorsun — bu bir seçim değil, filtre.",
            "en": "You can't bring an ugly sentence to your lips — this isn't a choice, it's a filter.",
        },
        "emotional_intent": "izin",
        "tone_accent": "blush",
        "trigger": {
            "kind": "aspect",
            "planet_a": "Mercury",
            "planet_b": "Venus",
            "aspect": "conjunction",
            "orb_max": 3.0,
        },
        "priority_kind": "tight_aspect_1_to_3",
        "section_binding": "identity_mechanics",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 1,
                "planet_filter": "venus_only",
                "templates": {
                    "tr": [
                        "Bugün küçük bir pürüz gözüne takılıyor. Görmek istemesen de.",
                    ],
                    "en": [
                        "A small imperfection catches your eye today. Even when you'd rather not notice.",
                    ],
                },
            },
        ],
    },
    {
        "id": "sun_h12_behind_the_scenes",
        "name": "Perde arkası çalışma",
        "opening": {
            "tr": "Emeğinin yüzde doksanını kimse görmüyor — ve sen göstermeye de çalışmıyorsun.",
            "en": "Ninety percent of your work goes unseen — and you're not trying to show it either.",
        },
        "emotional_intent": "fark_edilme",
        "tone_accent": "lav",
        "trigger": {"kind": "placement", "planet": "Sun", "house": 12},
        "priority_kind": "placement",
        "section_binding": "career_visibility",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 12,
                "planet_filter": "fast",
                "templates": {
                    "tr": [
                        "Bu akşam içine çekilmek iyi gelir. Asıl işin zaten sessiz yerde büyüyor.",
                    ],
                    "en": [
                        "Pulling inward feels right tonight. The real work is already growing somewhere quiet.",
                    ],
                },
            },
        ],
    },
    {
        "id": "sun_sq_saturn_early_responsibility",
        "name": "Erken sorumluluk",
        "opening": {
            "tr": "Çocukken büyük davranmayı öğrendin; şimdi küçük olmak tuhaf geliyor.",
            "en": "As a child you learned to act grown; now being small feels strange.",
        },
        "emotional_intent": "rahatlatma",
        "tone_accent": "lime",
        "trigger": {
            "kind": "aspect",
            "planet_a": "Sun",
            "planet_b": "Saturn",
            "aspect": "square",
            "orb_max": 5.0,
        },
        "priority_kind": "tight_aspect_1_to_3",
        "section_binding": "identity_mechanics",
        "why_now_triggers": [
            {
                "kind": "transit_to_pattern_body",
                "target_planet": "Saturn",
                "transit_planet_filter": "Sun",
                "aspect": "any",
                "orb_max": 6.0,
                "templates": {
                    "tr": [
                        "Bugün omzunda bir ağırlık var, kimse koymadı — onu uzun zamandır sen taşıyorsun.",
                        "Bugün kimse bir şey yüklememişken ağır hissediyorsun. Eski bir alışkanlık hatırlamış.",
                    ],
                    "en": [
                        "There's a weight on your shoulders today that no one placed there — you've been carrying it for a long time.",
                        "No one put anything on you today, but you still feel the weight. An old habit remembering itself.",
                    ],
                },
            },
        ],
    },
    {
        "id": "venus_h11_collective_aesthetic",
        "name": "Kolektif estetik",
        "opening": {
            "tr": "Güzel bulduğun şey yalnız kalmıyor — hep bir grubun güzeli oluyor.",
            "en": "What you find beautiful doesn't stay alone — it always becomes a group's beautiful.",
        },
        "emotional_intent": "icgoru",
        "tone_accent": "stone",
        "trigger": {"kind": "placement", "planet": "Venus", "house": 11},
        "priority_kind": "placement",
        "section_binding": "relationships_depth",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 11,
                "planet_filter": "venus_only",
                "templates": {
                    "tr": [
                        "Bu hafta beğendiğin bir şey başkasına da dokunuyor. Paylaşman için iyi zaman.",
                    ],
                    "en": [
                        "Something you love lands well with someone else this week. Good time to share.",
                    ],
                },
            },
        ],
    },
    {
        "id": "moon_h8_hidden_intensity",
        "name": "Gizli yoğunluk",
        "opening": {
            "tr": "Herkes seni sakin sanıyor — içerde ne döndüğünü kimseye söylemiyorsun.",
            "en": "Everyone thinks you're calm — you don't tell anyone what's happening inside.",
        },
        "emotional_intent": "izin",
        "tone_accent": "blush",
        "trigger": {"kind": "placement", "planet": "Moon", "house": 8},
        "priority_kind": "placement",
        "section_binding": "relationships_depth",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 8,
                "planet_filter": "fast",
                "templates": {
                    "tr": [
                        "Bugün dışarıdan her şey yerinde. İçeride değil — saklamak bile başlı başına iş.",
                        "Bugün yüzeyde bir şey yokmuş gibi. İçeride var — ve göstermemek bile yorucu.",
                    ],
                    "en": [
                        "On the outside, everything's in place today. Inside, it's not — and hiding that is its own kind of work.",
                        "On the surface, nothing's happening today. Inside, something is — not showing it is tiring on its own.",
                    ],
                },
            },
        ],
    },
    {
        "id": "mars_h6_disciplined_energy",
        "name": "Disiplinli enerji",
        "opening": {
            "tr": "Rastgele hareket etmiyorsun — her enerji bir rutinden geçiyor.",
            "en": "You don't move randomly — every bit of energy goes through a routine.",
        },
        "emotional_intent": "ayrim",
        "tone_accent": "lime_lav",
        "trigger": {"kind": "placement", "planet": "Mars", "house": 6},
        "priority_kind": "placement",
        "section_binding": "direction_learning",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 6,
                "planet_filter": "mars_only",
                "templates": {
                    "tr": [
                        "Bu akşam küçük bir işi tamamen bitirmek iyi gelir. Yarım kalanlar bugün seni yoruyor.",
                    ],
                    "en": [
                        "Finishing one small thing completely tonight will feel good. Half-done things are tiring you today.",
                    ],
                },
            },
        ],
    },
    {
        "id": "capricorn_asc_leo_moon_serious_warm",
        "name": "Ciddi görünüş / sıcak iç",
        "opening": {
            "tr": "Sana mesafeli diyorlar — içerde bakılmayı bekleyen bir tarafın var.",
            "en": "They call you distant — inside, there's a part of you waiting to be seen.",
        },
        "emotional_intent": "fark_edilme",
        "tone_accent": "lav",
        "trigger": {
            "kind": "compound",
            "asc_sign": "Capricorn",
            "moon_sign": "Leo",
        },
        "priority_kind": "angular",
        "section_binding": "identity_mechanics",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 1,
                "planet_filter": "sun_only",
                "templates": {
                    "tr": [
                        "Bugün bir yanın görünmek istiyor, bir yanın beklemek. İkisine de hak ver — ikisi de senin.",
                        "Bugün hem öne çıkmak hem geride durmak istiyorsun. İkisi de senden.",
                    ],
                    "en": [
                        "Today one side of you wants to be seen, another wants to wait. Hold both — both are yours.",
                        "Today you want to step forward and stay back at the same time. Both come from you.",
                    ],
                },
            },
        ],
    },
    {
        "id": "stellium_h1_identity_weight",
        "name": "Kimlik ağırlığı",
        "opening": {
            "tr": "Odaya girdiğinde kimse fark etmese bile odanın tonu değişiyor.",
            "en": "Even when no one notices you enter a room, the room's tone shifts.",
        },
        "emotional_intent": "icgoru",
        "tone_accent": "stone",
        "trigger": {"kind": "stellium", "house": 1, "min_count": 3},
        "priority_kind": "stellium",
        "section_binding": "identity_mechanics",
        "why_now_triggers": [
            {
                "kind": "transit_through_house",
                "house": 1,
                "planet_filter": "sun_only",
                "templates": {
                    "tr": [
                        "Bu hafta bir odaya girdiğinde ortam seninle hafiften değişiyor. Alışman biraz zaman alabilir.",
                        "Bu hafta bir odaya girdiğinde ortam seninle hafiften değişiyor. Alışmak zaman istiyor.",
                    ],
                    "en": [
                        "When you walk into a room this week, the air shifts with you. Takes a minute to get used to.",
                        "When you walk into a room this week, the air shifts with you. Getting used to it takes time.",
                    ],
                },
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Helper accessors — keep pattern lookup cheap and immutable-friendly.
# ---------------------------------------------------------------------------


def pattern_index() -> Dict[str, Dict[str, Any]]:
    """Return {pattern_id: pattern_dict} map for O(1) lookup."""
    return {entry["id"]: dict(entry) for entry in PATTERN_LIBRARY}


def pattern_ids() -> List[str]:
    """All pattern IDs in library order."""
    return [entry["id"] for entry in PATTERN_LIBRARY]


def get_tone_accent(intent: str) -> str:
    """Intent → tone_accent UI driver. Unknown intent → 'stone' safe default."""
    return INTENT_TO_TONE_ACCENT.get(intent, "stone")


def get_voice_shift(intent: str) -> Dict[str, float]:
    """Intent → voice_profile_v2 axis override (per-thread only)."""
    return dict(INTENT_VOICE_SHIFT.get(intent, {}))


def priority_rank_value(pattern: Mapping[str, Any]) -> int:
    """Stable sort key — lower is higher priority. Unknown priority_kind → 99."""
    kind = pattern.get("priority_kind", "placement")
    return PRIORITY_RANKS.get(kind, 99)


# ---------------------------------------------------------------------------
# Why-now rendering — first match wins, no scoring.
# ---------------------------------------------------------------------------


def _stable_pick(options: List[str], seed: str) -> str:
    """Deterministic selection from a template pool — same user, same output."""
    if not options:
        return ""
    import hashlib
    idx = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16) % len(options)
    return options[idx]


def render_why_now_for_trigger(
    trigger: Mapping[str, Any],
    locale: str,
    seed: str,
) -> str:
    """Pick a deterministic human-first why_now line from a matched trigger's pool.

    Voice Contract v3 §4 — human-first, first match wins, no scoring.
    Empty string if templates missing (safer than None — UI downstream
    expects str, never null).
    """
    templates = trigger.get("templates", {})
    pool = templates.get(locale) or templates.get("tr") or []
    return _stable_pick(list(pool), seed=seed + ":" + str(trigger.get("kind", "")))
