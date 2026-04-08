from app.transit.narrative.deep_archetype_engine import build_active_event_cards, build_event_card
from app.transit.narrative.text_quality_tr import rewrite_period_card_tr, why_now_tr


def _natal_snapshot() -> dict:
    return {
        "bodies": [
            {"body": "Sun", "lon": 276.75, "sign": "Capricorn", "house": 1},
            {"body": "Moon", "lon": 133.94, "sign": "Leo", "house": 8},
            {"body": "Mercury", "lon": 287.36, "sign": "Capricorn", "house": 1, "rx": True},
            {"body": "Venus", "lon": 253.71, "sign": "Sagittarius", "house": 12},
            {"body": "Mars", "lon": 177.93, "sign": "Virgo", "house": 9},
            {"body": "Jupiter", "lon": 294.29, "sign": "Capricorn", "house": 1},
            {"body": "Saturn", "lon": 1.15, "sign": "Aries", "house": 3},
            {"body": "Uranus", "lon": 303.06, "sign": "Aquarius", "house": 1},
            {"body": "Neptune", "lon": 296.69, "sign": "Capricorn", "house": 1},
            {"body": "Pluto", "lon": 244.25, "sign": "Sagittarius", "house": 11},
        ],
        "angles": {
            "ASC": {"point": "ASC", "sign": "Capricorn"},
            "MC": {"point": "MC", "sign": "Libra"},
            "DSC": {"point": "DSC", "sign": "Cancer"},
            "IC": {"point": "IC", "sign": "Aries"},
        },
        "house_cusps": [
            {"house": 1, "sign": "Capricorn"},
            {"house": 2, "sign": "Aquarius"},
            {"house": 3, "sign": "Pisces"},
            {"house": 4, "sign": "Aries"},
            {"house": 5, "sign": "Taurus"},
            {"house": 6, "sign": "Gemini"},
            {"house": 7, "sign": "Cancer"},
            {"house": 8, "sign": "Leo"},
            {"house": 9, "sign": "Virgo"},
            {"house": 10, "sign": "Libra"},
            {"house": 11, "sign": "Scorpio"},
            {"house": 12, "sign": "Sagittarius"},
        ],
    }


def _event_neptune_square_asc() -> dict:
    return {
        "event_id": "evt_neptune_asc",
        "transit_body": "Neptune",
        "natal_point": "ASC",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.17,
        "houses": {"transit_in_natal_house": 3, "natal_point_house": 1},
        "domains": ["identity"],
        "ranking": {"tier": "main", "weight": 1.3},
        "strength": 0.92,
    }


def _event_neptune_square_dsc() -> dict:
    return {
        "event_id": "evt_neptune_dsc",
        "transit_body": "Neptune",
        "natal_point": "DSC",
        "aspect": "square",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.9,
        "houses": {"transit_in_natal_house": 3, "natal_point_house": 7},
        "domains": ["relationships"],
        "ranking": {"tier": "main", "weight": 1.2},
        "strength": 0.88,
    }


def _event_uranus_trine_mars() -> dict:
    return {
        "event_id": "evt_uranus_mars",
        "transit_body": "Uranus",
        "natal_point": "Mars",
        "aspect": "trine",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.8,
        "houses": {"transit_in_natal_house": 5, "natal_point_house": 9},
        "domains": ["meaning_learning"],
        "ranking": {"tier": "main", "weight": 1.3},
        "strength": 0.91,
    }


def _event_pluto_sextile_pluto() -> dict:
    return {
        "event_id": "evt_pluto_pluto",
        "transit_body": "Pluto",
        "natal_point": "Pluto",
        "aspect": "sextile",
        "phase": "applying",
        "bucket": "long",
        "orb_deg": 0.6,
        "houses": {"transit_in_natal_house": 1, "natal_point_house": 11},
        "domains": ["social_future"],
        "ranking": {"tier": "main", "weight": 1.15},
        "strength": 0.87,
    }


def test_event_card_exposes_gold_schema_fields() -> None:
    card = build_event_card(_event_neptune_square_asc(), context={"natal": _natal_snapshot()})
    for key in (
        "headline",
        "opening",
        "essence",
        "mechanism",
        "asks",
        "watchout",
        "what_it_builds",
        "technical_note",
    ):
        assert isinstance(card.get(key), str) and str(card.get(key)).strip()


def test_neptune_square_asc_copy_is_human_and_clear() -> None:
    card = build_event_card(_event_neptune_square_asc(), context={"natal": _natal_snapshot()})
    merged = " ".join(
        str(card.get(key) or "")
        for key in ("headline", "opening", "essence", "mechanism", "asks", "watchout", "what_it_builds")
    ).lower()
    assert "nasıl duyulduğun" in merged
    assert "iletişim" in merged or "konuşma" in merged
    assert "dışarıda" in merged or "ilk izlenim" in merged
    for banned in ("orb", "phase", "bucket", "exact", "applying", "arka bağlantı", "tema ile çalışır"):
        assert banned not in merged


def test_neptune_square_asc_mechanism_names_aspect_and_houses() -> None:
    card = build_event_card(_event_neptune_square_asc(), context={"natal": _natal_snapshot()})
    mechanism = str(card.get("mechanism") or "").lower()
    assert "kare açı" in mechanism or "kare" in mechanism
    assert "3. ev" in mechanism
    assert "1. ev" in mechanism
    assert any(token in mechanism for token in ("yükselen", "kimlik", "iletişim"))


def test_uranus_trine_mars_respects_5_to_9_priority() -> None:
    card = build_event_card(_event_uranus_trine_mars(), context={"natal": _natal_snapshot()})
    mechanism = str(card.get("mechanism") or "").lower()
    watchout = str(card.get("watchout") or "").lower()
    technical = str(card.get("technical_note") or "").lower()

    assert any(token in mechanism for token in ("yaratıcılık", "görünür üretim", "keyif"))
    assert any(token in mechanism for token in ("öğrenme", "uzmanlaşma", "yön duygusu"))
    assert "4. ev" not in watchout
    assert "11. ev" not in watchout
    assert "4. ev" not in mechanism
    assert "11. ev" not in mechanism
    assert card["headline"].startswith("İlhamını Yönteme Çeviriyorsun")
    assert "ilhamı çalışır bir yönteme" in str(card.get("what_it_builds") or "").lower()
    if technical:
        assert any(token in technical for token in ("5. ev", "9. ev"))


def test_pluto_sextile_pluto_keeps_its_own_voice() -> None:
    card = build_event_card(_event_pluto_sextile_pluto(), context={"natal": _natal_snapshot()})
    opening = str(card.get("opening") or "").lower()
    essence = str(card.get("essence") or "").lower()
    assert "nasıl duyulduğun" not in opening
    assert "muğlak" not in opening
    assert "çevre" in opening or "hedef" in opening
    assert "seçici" in essence or "stratejik" in essence


def test_watchout_contains_actual_risk_not_spillover() -> None:
    card = build_event_card(_event_uranus_trine_mars(), context={"natal": _natal_snapshot()})
    watchout = str(card.get("watchout") or "").lower()
    assert any(token in watchout for token in ("risk", "dağı", "heyecan", "ölçü"))
    for banned in ("4. ev", "11. ev", "arkadaş çevresi", "ev düzeni"):
        assert banned not in watchout


def test_active_event_cards_do_not_append_generic_watchout_when_event_risk_exists() -> None:
    report = {
        "display": {
            "items": [
                _event_neptune_square_dsc(),
                _event_uranus_trine_mars(),
                _event_pluto_sextile_pluto(),
            ]
        },
        "natal": _natal_snapshot(),
    }
    cards = build_active_event_cards(report, max_cards=3)
    neptune_card = next(card for card in cards if card.get("event_id") == "evt_neptune_dsc")
    watch_list = [str(item).strip() for item in (neptune_card.get("watch_out") or []) if str(item).strip()]
    assert watch_list
    assert "Aşırı yüklenme." not in watch_list
    assert "Odak kaybı." not in watch_list
    assert "Acele karar." not in watch_list


def test_cards_in_same_period_keep_distinct_openings() -> None:
    report = {
        "display": {
            "items": [
                _event_neptune_square_asc(),
                _event_uranus_trine_mars(),
                _event_pluto_sextile_pluto(),
                _event_neptune_square_dsc(),
            ]
        },
        "natal": _natal_snapshot(),
    }
    cards = build_active_event_cards(report, max_cards=4)
    openings = [str(card.get("opening") or card.get("teaser") or "").strip() for card in cards]
    assert len(openings) == len(set(openings))


def test_rewrite_period_card_tr_adds_period_fields_without_flattening_event_voice() -> None:
    base = build_event_card(_event_uranus_trine_mars(), context={"natal": _natal_snapshot()})
    out = rewrite_period_card_tr(base, event=_event_uranus_trine_mars())
    assert isinstance(out.get("period_opening"), str) and out["period_opening"]
    assert isinstance(out.get("relational_or_life_expression"), str) and out["relational_or_life_expression"]
    assert isinstance(out.get("what_it_builds"), str) and out["what_it_builds"]
    assert "öğrenme" in str(out.get("mechanism") or "").lower() or "uzmanlaşma" in str(out.get("mechanism") or "").lower()
    assert "muğlak" not in str(out.get("opening") or "").lower()


def test_no_mechanical_phrase_regressions_in_primary_fields() -> None:
    card = build_event_card(_event_neptune_square_asc(), context={"natal": _natal_snapshot()})
    merged = " ".join(
        str(card.get(key) or "")
        for key in ("headline", "opening", "essence", "mechanism", "asks", "watchout")
    ).lower()
    banned_phrases = (
        "sesin ve duruşun",
        "akış açık",
        "ilk tepkiyi ritme çevirmek",
        "ritim kurdukça netleşir",
    )
    for banned in banned_phrases:
        assert banned not in merged


def test_why_now_tr_stays_human_readable() -> None:
    text = why_now_tr(_event_neptune_square_asc())
    assert "+" not in text
    assert "kimlik hattı aktif" in text.lower()
    assert any(token in text.lower() for token in ("katman katman", "gündemde", "belirgin", "odakta"))
