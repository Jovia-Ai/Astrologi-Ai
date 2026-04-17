from app.transit.narrative.phrase_lib_tr import (
    PERIOD_TRACK_COPY_TR,
    PLANET_ARCHETYPES_TR,
    PROMISE_DOMAIN_CONTEXT_TR,
    SIGN_STYLES_TR,
    compose_phrase_pack,
)


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


# S0-2: PLANET_ARCHETYPES_TR — 10 gezegen coverage + frozen baseline + shape + blocklist + length.

_PLANET_ARCHETYPES_BASELINE = {
    "uranus": {
        "verbs": ("sarsar", "uyandırır", "yeni yol açar"),
        "shadow": ("sabırsız kopuş", "ani karar", "kanal dağılması"),
        "gift": ("yaratıcı sıçrama", "elektrik netlik", "yenilik cesareti"),
    },
    "neptune": {
        "verbs": ("bulanıklaştırır", "yumuşatır", "sezdirir"),
        "shadow": ("sınır erimesi", "projeksiyon", "yanlış okuma"),
        "gift": ("sezgiyi ayıklama", "nazik sınır", "ilhamlı netlik"),
    },
    "mars": {
        "verbs": ("başlatır", "iter", "hamleyi açar"),
        "shadow": ("acele", "sertleşme", "tepkisellik"),
        "gift": ("doğru hamle", "cesur netlik", "odak"),
    },
    "saturn": {
        "verbs": ("test eder", "sıkılaştırır", "olgunlaştırır"),
        "shadow": ("katılık", "aşırı yük", "yavaş kilitlenme"),
        "gift": ("ustalık", "kalıcı sistem", "iç otorite"),
    },
}


def test_planet_archetypes_covers_all_ten_planets() -> None:
    expected = {
        "sun", "moon", "mercury", "venus", "mars",
        "jupiter", "saturn", "uranus", "neptune", "pluto",
    }
    assert set(PLANET_ARCHETYPES_TR.keys()) == expected


def test_planet_archetypes_existing_values_are_frozen() -> None:
    for planet, baseline in _PLANET_ARCHETYPES_BASELINE.items():
        assert PLANET_ARCHETYPES_TR[planet] == baseline, (
            f"{planet} baseline değişti; regression."
        )


def test_planet_archetypes_entries_have_required_shape() -> None:
    for planet, entry in PLANET_ARCHETYPES_TR.items():
        assert set(entry.keys()) == {"verbs", "shadow", "gift"}, planet
        for key, values in entry.items():
            assert isinstance(values, tuple) and len(values) == 3, f"{planet}.{key} 3-tuple değil"
            for v in values:
                assert isinstance(v, str) and v.strip(), f"{planet}.{key} boş değer"


def test_planet_archetypes_no_blocklist_jargon() -> None:
    for planet, entry in PLANET_ARCHETYPES_TR.items():
        merged = " ".join(v for values in entry.values() for v in values).lower()
        for banned in _SIGN_STYLES_BLOCKLIST:
            assert banned not in merged, f"{planet} içinde yasaklı ifade: {banned}"


def test_planet_archetypes_value_length_guard() -> None:
    # editorial disiplin: her değer ≤ 32 karakter, ≤ 4 kelime
    for planet, entry in PLANET_ARCHETYPES_TR.items():
        for key, values in entry.items():
            for v in values:
                assert len(v) <= 32, f"{planet}.{key} çok uzun: '{v}'"
                assert len(v.split()) <= 4, f"{planet}.{key} çok fazla kelime: '{v}'"


# S0-3: PERIOD_TRACK_COPY_TR — 9 track coverage (default dahil), mevcut 4 + default
# frozen, yeni 5 track'in shape/field/version doğruluğu, blocklist.

_PERIOD_TRACK_REQUIRED_FIELDS = {
    "period_opening",
    "big_picture",
    "mechanism",
    "growth_edge",
    "relational_or_life_expression",
    "what_it_builds",
}

_PERIOD_TRACK_BASELINE_KEYS = {
    "identity_spine",
    "method_shift_9_virgo",
    "network_transform_11",
    "mirror_axis_1_7",
    "default",
}

_PERIOD_TRACK_NEW_KEYS = {
    "resource_axis_2_8",
    "healing_axis_6_12",
    "creativity_5",
    "root_4",
    "dissolution_12",
}


def test_period_track_covers_nine_keys() -> None:
    expected = _PERIOD_TRACK_BASELINE_KEYS | _PERIOD_TRACK_NEW_KEYS
    assert set(PERIOD_TRACK_COPY_TR.keys()) == expected


def test_period_track_baseline_tracks_exist_and_keep_version_v2() -> None:
    # Mevcut 4 track + default hâlâ var ve version='v2'. İçerik kontrolü aşağıda.
    for key in _PERIOD_TRACK_BASELINE_KEYS:
        assert key in PERIOD_TRACK_COPY_TR, f"{key} track'i kaybolmuş"
        assert PERIOD_TRACK_COPY_TR[key].get("version") == "v2", key


def test_period_track_identity_spine_frozen_snapshot() -> None:
    # identity_spine — tam içerik frozen (regression).
    track = PERIOD_TRACK_COPY_TR["identity_spine"]
    assert track["period_opening"] == (
        "Bu dönem önce kendini nasıl anlattığın değişiyor, sonra bunun etkisi dışarıda nasıl göründüğüne yansıyor.",
        "Şu sıralar mesele daha çok görünmek değil; daha anlaşılır, daha tutarlı görünmek.",
    )
    assert track["what_it_builds"] == (
        "Bu dönem sende kendini daha net ifade etme kasını geliştiriyor.",
        "Bu dönem sende yanlış anlaşılma payını azaltan daha temiz bir ifade kası kuruyor.",
    )


def test_period_track_default_frozen_snapshot() -> None:
    # default catchall — tam içerik frozen.
    track = PERIOD_TRACK_COPY_TR["default"]
    assert track["period_opening"] == (
        "Bu dönem hayatının bir alanı daha görünür hale geliyor ve senden daha bilinçli seçimler istiyor.",
    )
    assert track["what_it_builds"] == (
        "Bu dönem sende daha net seçim yapma kasını geliştiriyor.",
    )


def test_period_track_new_tracks_have_required_shape() -> None:
    # Yeni 5 track: version=v2 + 6 required field + her field >=1 varyant (tuple).
    for key in _PERIOD_TRACK_NEW_KEYS:
        track = PERIOD_TRACK_COPY_TR[key]
        assert track.get("version") == "v2", key
        missing = _PERIOD_TRACK_REQUIRED_FIELDS - set(track.keys())
        assert not missing, f"{key} eksik alan: {missing}"
        for field in _PERIOD_TRACK_REQUIRED_FIELDS:
            values = track[field]
            assert isinstance(values, tuple) and len(values) >= 1, f"{key}.{field} tuple değil veya boş"
            for v in values:
                assert isinstance(v, str) and v.strip(), f"{key}.{field} boş cümle"


def test_period_track_new_tracks_have_two_variants_per_field() -> None:
    # Yeni 5 track her field için tam 2 varyant (roadmap spec).
    for key in _PERIOD_TRACK_NEW_KEYS:
        track = PERIOD_TRACK_COPY_TR[key]
        for field in _PERIOD_TRACK_REQUIRED_FIELDS:
            assert len(track[field]) == 2, f"{key}.{field} 2 varyant değil"


def test_period_track_all_content_blocklist_clean() -> None:
    # 9 track × tüm cümleler, yasak editorial jargon içermemeli.
    for key, track in PERIOD_TRACK_COPY_TR.items():
        for field in _PERIOD_TRACK_REQUIRED_FIELDS:
            values = track.get(field, ())
            merged = " ".join(values).lower()
            for banned in _SIGN_STYLES_BLOCKLIST:
                assert banned not in merged, f"{key}.{field} içinde yasak ifade: {banned}"


# S0-4: PROMISE_DOMAIN_CONTEXT_TR — 6 domain coverage + shape + blocklist.

_PROMISE_DOMAIN_EXPECTED = {"career", "identity", "relationships", "home", "mind", "inner"}


def test_promise_domain_context_covers_six_known_domains() -> None:
    # "general" KASITLI hariç — o durumda prefix eklenmiyor.
    assert set(PROMISE_DOMAIN_CONTEXT_TR.keys()) == _PROMISE_DOMAIN_EXPECTED


def test_promise_domain_context_two_variants_per_domain() -> None:
    for domain, variants in PROMISE_DOMAIN_CONTEXT_TR.items():
        assert isinstance(variants, tuple) and len(variants) == 2, domain
        for v in variants:
            assert isinstance(v, str) and v.strip(), domain


def test_promise_domain_context_blocklist_clean() -> None:
    for domain, variants in PROMISE_DOMAIN_CONTEXT_TR.items():
        merged = " ".join(variants).lower()
        for banned in _SIGN_STYLES_BLOCKLIST:
            assert banned not in merged, f"{domain} içinde yasak ifade: {banned}"


def test_promise_domain_context_does_not_start_with_bu_donem() -> None:
    # A seçeneği 3-cümle durumunda "Bu dönem" tekrarını önlemek için prefix
    # farklı bir sesle başlamalı (Haritanda/Natal/Kimlik/Kök/Zihin/İç dünya).
    for domain, variants in PROMISE_DOMAIN_CONTEXT_TR.items():
        for v in variants:
            assert not v.lower().startswith("bu dönem"), (
                f"{domain} prefix 'Bu dönem' ile başlıyor — tekrar riski"
            )



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
    # Editorial tone refactor (commit 3e60237): "9. Ev" teknik terimi artık
    # semantic ev temasıyla değiştiriliyor (öğrenme / yön / ufuk / uzmanlaşma).
    # Sign tr adı hâlâ aynen korunuyor.
    assert "Başak" in merged
    house_9_themes = ("öğrenme", "yön", "ufuk", "uzmanlaşma")
    assert any(theme in merged.lower() for theme in house_9_themes), (
        f"9. ev teması semantic olarak bulunmadı: {merged}"
    )


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
        # Editorial tone refactor (commit 3e60237): _build_why_now artık "Orb" /
        # "süren etki" gibi teknik terimler yerine semantic orb_phrase +
        # duration_phrase + angle_phrase üretiyor (phrase_lib_tr.py:1043).
        # Minimum olarak bir etki/tema markörü + süre ifadesi içermeli.
        lower_now = why_now.lower()
        assert any(m in lower_now for m in ("etki", "tema", "dalga", "vurgu")), (
            f"why_now temporal marker yok: {why_now}"
        )
        assert any(m in lower_now for m in ("sürebilir", "sürdür", "kalabilir", "çalışır", "pencere")), (
            f"why_now süre ifadesi yok: {why_now}"
        )
        for token in ("south node", "north node", "lilith", "vertex", "fortune", "chiron"):
            assert token not in lower_now
