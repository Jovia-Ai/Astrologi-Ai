from app.transit.narrative.phrase_lib_tr import SIGN_STYLES_TR, compose_phrase_pack


# S0-1: 12 burç coverage, mevcut 5 burcun değerlerinin frozen (regression) olduğu,
# editorial blocklist ve length guard'larını doğrulayan testler.

_SIGN_STYLES_BASELINE = {
    "virgo": {"style": "metod ve iyileştirme", "pitfall": "mükemmellik ertelemesi", "superpower": "ölçülü ustalık"},
    "capricorn": {"style": "yapı ve sorumluluk", "pitfall": "aşırı kontrol", "superpower": "sürdürülebilir sonuç"},
    "aries": {"style": "ilk hamle", "pitfall": "acele patlama", "superpower": "cesur başlatma"},
    "aquarius": {"style": "yenilik", "pitfall": "ani kopuş", "superpower": "yaratıcı sıçrama"},
    "pisces": {"style": "sezgi", "pitfall": "sınır erimesi", "superpower": "ince duyarlık"},
}

_SIGN_STYLES_BLOCKLIST = (
    "enerji",
    "evren sana",
    "çakra",
    "frekans",
    "titreşim",
    "etkisi altında",
)


def test_sign_styles_covers_all_twelve_signs() -> None:
    expected = {
        "aries", "taurus", "gemini", "cancer", "leo", "virgo",
        "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
    }
    assert set(SIGN_STYLES_TR.keys()) == expected


def test_sign_styles_existing_values_are_frozen() -> None:
    for sign, baseline in _SIGN_STYLES_BASELINE.items():
        assert SIGN_STYLES_TR[sign] == baseline, (
            f"{sign} baseline değişti; regression."
        )


def test_sign_styles_entries_have_required_keys() -> None:
    for sign, entry in SIGN_STYLES_TR.items():
        assert set(entry.keys()) == {"style", "pitfall", "superpower"}, sign
        for key, value in entry.items():
            assert isinstance(value, str) and value.strip(), f"{sign}.{key} boş"


def test_sign_styles_no_blocklist_jargon() -> None:
    for sign, entry in SIGN_STYLES_TR.items():
        merged = " ".join(entry.values()).lower()
        for banned in _SIGN_STYLES_BLOCKLIST:
            assert banned not in merged, f"{sign} içinde yasaklı ifade: {banned}"


def test_sign_styles_value_length_guard() -> None:
    # editorial disiplin: her tamlama ≤ 32 karakter, ≤ 4 kelime
    for sign, entry in SIGN_STYLES_TR.items():
        for key, value in entry.items():
            assert len(value) <= 32, f"{sign}.{key} çok uzun: '{value}'"
            assert len(value.split()) <= 4, f"{sign}.{key} çok fazla kelime: '{value}'"



def _context_pack_mars_virgo_9() -> dict:
    return {
        "target": {"planet": "Mars", "house": 9, "sign": "virgo", "sign_tr": "Başak"},
        "dispositor": {"planet": "Mercury", "house": 1, "sign": "capricorn"},
        "rulership_houses": [
            {"house": 4, "sign": "aries"},
            {"house": 11, "sign": "scorpio"},
        ],
    }


def _event_uranus_trine_mars() -> dict:
    return {
        "event_id": "evt_uranus_mars_phrase",
        "transit_body": "Uranus",
        "aspect": "trine",
        "natal_point": "Mars",
        "houses": {"transit_in_natal_house": 5},
    }


def test_phrase_pack_is_deterministic() -> None:
    pack_a = compose_phrase_pack(
        transit_body="Uranus",
        aspect="trine",
        natal_point="Mars",
        context_pack=_context_pack_mars_virgo_9(),
        event=_event_uranus_trine_mars(),
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )
    pack_b = compose_phrase_pack(
        transit_body="Uranus",
        aspect="trine",
        natal_point="Mars",
        context_pack=_context_pack_mars_virgo_9(),
        event=_event_uranus_trine_mars(),
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )
    assert pack_a == pack_b


def test_phrase_pack_contains_basak_and_9th_house_context() -> None:
    pack = compose_phrase_pack(
        transit_body="Uranus",
        aspect="trine",
        natal_point="Mars",
        context_pack=_context_pack_mars_virgo_9(),
        event=_event_uranus_trine_mars(),
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )
    merged = " ".join(
        [
            str(pack.get("scene_line") or ""),
            str(pack.get("conflict_add") or ""),
            str(pack.get("upper_add") or ""),
            " ".join(str(x) for x in pack.get("guidance_add", [])),
        ]
    )
    assert "Başak" in merged
    assert "9. Ev" in merged


def test_phrase_pack_has_no_banned_tokens() -> None:
    pack = compose_phrase_pack(
        transit_body="Neptune",
        aspect="square",
        natal_point="ASC",
        context_pack={"target": {"planet": "ASC", "house": 1, "sign": "capricorn", "sign_tr": "Oğlak"}},
        event={"event_id": "evt_np_asc", "houses": {"transit_in_natal_house": 3}},
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )
    merged = " ".join(
        [
            str(pack.get("title") or ""),
            str(pack.get("scene_line") or ""),
            str(pack.get("conflict_add") or ""),
            str(pack.get("shadow_add") or ""),
            str(pack.get("upper_add") or ""),
            " ".join(str(x) for x in pack.get("guidance_add", [])),
            " ".join(str(x) for x in pack.get("watch_out_add", [])),
        ]
    ).lower()
    for token in ("south node", "north node", "lilith", "vertex", "fortune", "chiron"):
        assert token not in merged


def test_phrase_pack_sentence_caps() -> None:
    pack = compose_phrase_pack(
        transit_body="Uranus",
        aspect="trine",
        natal_point="Mars",
        context_pack=_context_pack_mars_virgo_9(),
        event=_event_uranus_trine_mars(),
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )

    def _count_sentences(text: str) -> int:
        normalized = text.replace("!", ".").replace("?", ".")
        normalized = normalized.replace("1.", "1").replace("2.", "2").replace("3.", "3")
        normalized = normalized.replace("4.", "4").replace("5.", "5").replace("6.", "6")
        normalized = normalized.replace("7.", "7").replace("8.", "8").replace("9.", "9")
        normalized = normalized.replace("10.", "10").replace("11.", "11").replace("12.", "12")
        return len([p for p in normalized.split(".") if p.strip()])

    assert _count_sentences(str(pack.get("conflict_add") or "")) <= 2
    assert _count_sentences(str(pack.get("shadow_add") or "")) <= 2
    assert _count_sentences(str(pack.get("upper_add") or "")) <= 2


def test_phrase_pack_aspect_section_mapping() -> None:
    pack = compose_phrase_pack(
        transit_body="Uranus",
        aspect="trine",
        natal_point="Mars",
        context_pack=_context_pack_mars_virgo_9(),
        event=_event_uranus_trine_mars(),
        max_len={"conflict": 2, "shadow": 2, "upper": 2},
    )
    assert pack["conflict_label"] == "Akış"
    assert pack["conflict_tone"] == "flow"


def test_phrase_pack_tone_section_labels_and_why_now() -> None:
    cases = [
        ("trine", "flow", "Akış"),
        ("sextile", "chance", "Fırsat"),
        ("square", "friction", "Sürtünme"),
        ("opposition", "mirror", "Ayna"),
        ("conjunction", "focus", "Yoğunluk"),
    ]
    for aspect, tone, conflict_label in cases:
        pack = compose_phrase_pack(
            transit_body="Saturn",
            aspect=aspect,
            natal_point="ASC",
            context_pack={"target": {"planet": "ASC", "house": 1, "sign": "capricorn", "sign_tr": "Oğlak"}},
            event={
                "event_id": f"evt_{aspect}",
                "natal_point": "ASC",
                "orb_deg": 0.4,
                "bucket": "long",
                "phase": "applying",
                "houses": {"transit_in_natal_house": 3},
            },
            max_len={"conflict": 2, "shadow": 2, "upper": 2},
        )
        assert pack["tone"] == tone
        assert pack["section_labels"]["conflict"] == conflict_label
        why_now = str(pack.get("why_now") or "")
        assert why_now.endswith(".")
        assert "Orb" in why_now
        assert "süren etki" in why_now
        for token in ("south node", "north node", "lilith", "vertex", "fortune", "chiron"):
            assert token not in why_now.lower()
