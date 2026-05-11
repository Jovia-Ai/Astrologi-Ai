from app.transit.narrative.daily_synthesis import build_daily_synthesis


def _card(
    event_id: str,
    *,
    transit_body: str = "Mercury",
    natal_point: str = "Sun",
    aspect: str = "square",
    mode: str = "friction",
    house: int = 3,
    orb_deg: float = 0.6,
    phase: str = "exactish",
    felt: str = "Bugün söylediklerinin tonu daha çabuk büyüyebilir.",
    guidance: str = "İlk cümleyi göndermeden niyetini netleştir",
) -> dict:
    return {
        "event_id": event_id,
        "transit_body": transit_body,
        "natal_point": natal_point,
        "aspect": aspect,
        "aspect_mode": mode,
        "orb_deg": orb_deg,
        "phase": phase,
        "felt_line_tr": felt,
        "guidance_micro_tr": guidance,
        "house_touchpoint_tr": "zihnin ve konuşma halin" if house in {3, 9} else "karşı tarafla arandaki çizgi",
        "houses": {
            "transit_in_natal_house": house,
            "natal_point_house": house,
        },
        "timing": {
            "peak_date_utc": "2026-03-31T09:00:00+00:00",
        },
        "time": {
            "is_peaking_today": True,
            "is_rising_today": False,
            "is_releasing_today": False,
        },
        "natal_promise": {"score": 0.78},
        "derived_context": {
            "natal_target": {
                "house": house,
                "rulership_houses": [house],
            }
        },
        "semantic_core": {
            "target_house": house,
            "target_house_domain": "mind" if house in {3, 9} else "relationships",
            "source_house_domain": "mind" if house in {3, 9} else "relationships",
        },
        "domain_scores": {"mind": 0.64, "relationships": 0.18} if house in {3, 9} else {"relationships": 0.64, "mind": 0.18},
        "lens_projection": {
            "primary_domain": "mind" if house in {3, 9} else "relationships",
            "projected_scores": {"mind": 0.72, "relationships": 0.14}
            if house in {3, 9}
            else {"relationships": 0.72, "mind": 0.14},
        },
    }


def test_daily_synthesis_returns_empty_without_daily_cards() -> None:
    assert build_daily_synthesis(daily_event_cards=[], period_core={}, natal_snapshot={}) == {}


def test_daily_synthesis_uses_raw_aspect_house_and_trace_fields() -> None:
    out = build_daily_synthesis(
        daily_event_cards=[_card("evt_1"), _card("evt_2", house=9, orb_deg=1.4, phase="applying")],
        period_core={
            "title": "Zihinsel Otoriteni İnşa Ediyorsun",
            "core_story": "Bu dönem düşünce biçimini yeniden yapılandırıyor.",
        },
        natal_snapshot={"asc_sign": "Capricorn"},
    )

    assert out["theme"] == "communication_clarity_tension"
    assert out["theme_description"]
    assert "konuş" in out["headline"].lower()
    assert "zihnin ve konuşma halin" in out["body"]
    assert "kare" in out["body"].lower()
    assert "Zihinsel Otoriteni İnşa Ediyorsun" in out["body"]
    assert out["guidance"] == "İlk cümleyi göndermeden niyetini netleştir."
    assert out["sources"]["daily"] == ["evt_1", "evt_2"]
    assert out["sources"]["trace"]["transit_body"] == "Mercury"
    assert out["sources"]["trace"]["natal_point"] == "Sun"
    assert out["sources"]["trace"]["aspect"] == "square"
    assert out["sources"]["trace"]["orb_deg"] == 0.6
    assert out["sources"]["trace"]["target_house"] == 3
    assert out["sources"]["trace"]["peak_date_utc"] == "2026-03-31T09:00:00+00:00"
    assert out["primary_signal"]["aspect_mode"] == "friction"
    assert out["planner_debug"]["mode_resolution"]["mode"] == out["narrative_mode"]
    assert out["planner_debug"]["spine_resolution"]["source"] in {"period_story_debug", "primary_fallback"}
    assert "house_3" in out["sources"]["natal"]
    assert "natal_point_sun" in out["sources"]["natal"]
    assert "asc_sign_capricorn" in out["sources"]["natal"]


def test_daily_synthesis_square_uses_concrete_tension_language() -> None:
    out = build_daily_synthesis(
        daily_event_cards=[_card("evt_tension", aspect="square", mode="friction", house=7, felt="Bugün karşı tarafın tonu seni daha hızlı gerebilir.")],
        period_core={"title": "Yakınlıkta Yeni Denge"},
        natal_snapshot={},
    )

    merged = f"{out['headline']} {out['body']}".lower()
    assert any(token in merged for token in ("baskı", "zorlaş", "ger"))
    assert "ilişki" in merged or "karşı" in merged or "beklenti" in merged


def test_daily_synthesis_third_house_uses_communication_scene_language() -> None:
    out = build_daily_synthesis(
        daily_event_cards=[_card("evt_mind", house=3, aspect="square", mode="friction")],
        period_core={},
        natal_snapshot={},
    )

    merged = f"{out['headline']} {out['body']} {out['guidance']}".lower()
    assert any(token in merged for token in ("konuş", "mesaj", "karar", "cümle"))


def test_daily_synthesis_missing_astro_details_falls_back_safely() -> None:
    out = build_daily_synthesis(
        daily_event_cards=[
            {
                "event_id": "evt_fallback",
                "felt_line_tr": "Bugün bir şey seni daha hızlı durdurabilir.",
                "guidance_micro_tr": "Hemen yanıt verme",
            }
        ],
        period_core={"core_story": "Daha geniş bir dönemin içindesin."},
        natal_snapshot={},
    )

    assert out["headline"]
    assert out["body"]
    assert out["guidance"] == "Hemen yanıt verme."
    assert out["sources"]["daily"] == ["evt_fallback"]
    assert out["sources"]["trace"]["aspect"] is None
    assert out["primary_signal"]["transit_body"] is None


def test_daily_synthesis_resolves_period_spine_and_support_signal() -> None:
    trigger = _card(
        "evt_trigger",
        transit_body="Neptune",
        natal_point="Sun",
        aspect="square",
        mode="friction",
        house=1,
        felt="Bugün kendini net tutmak zorlaşabilir.",
        guidance="İlk tepkiyi yavaşlat",
    )
    support = _card(
        "evt_support",
        transit_body="North Node",
        natal_point="Sun",
        aspect="sextile",
        mode="opening",
        house=2,
        felt="Bugün değer duygun daha kolay toparlanabilir.",
        guidance="Açılan küçük fırsatı küçümseme",
    )

    out = build_daily_synthesis(
        daily_event_cards=[trigger],
        period_event_cards=[support],
        period_core={
            "title": "Kimliğini Yeniden Kuruyorsun",
            "featured_events": [trigger, support],
            "_period_story_debug": {
                "spine_event_id": "evt_trigger",
                "spine_role": "builder",
                "support_event_ids": ["evt_support"],
                "support_roles": ["peak"],
            },
        },
        natal_snapshot={"asc_sign": "Capricorn"},
    )

    assert out["narrative_mode"] == "mixed"
    assert out["period_spine"]["event_id"] == "evt_trigger"
    assert out["support_signal"]["event_id"] == "evt_support"
    assert out["sources"]["period_spine"] == [
        "evt_trigger",
        "transit_body_neptune",
        "natal_point_sun",
        "aspect_square",
    ]
    assert out["sources"]["support"] == [
        "evt_support",
        "transit_body_north_node",
        "natal_point_sun",
        "aspect_sextile",
    ]
    assert "değer duygun" in out["body"].lower()
    assert out["planner_debug"]["spine_resolution"]["source"] == "period_story_debug"
    assert out["planner_debug"]["support_resolution"]["source"] == "period_story_debug"
    assert out["planner_debug"]["support_resolution"]["score"] > 0.0
    assert "same_natal_point" in out["planner_debug"]["support_resolution"]["reasons"]
    assert out["planner_debug"]["mode_resolution"]["reason"] == "pressure_and_support_are_both_meaningful"


def test_daily_synthesis_prefers_cluster_support_ids_for_today_support() -> None:
    trigger = {
        **_card(
            "evt_trigger",
            transit_body="Saturn",
            natal_point="Mercury",
            aspect="square",
            mode="friction",
            house=3,
            felt="Bugün bir konuşmada sabrın daha hızlı zorlanabilir.",
            guidance="Cevabı uzatma",
        ),
        "cluster_support_event_ids": ["evt_cluster_support"],
    }
    support = _card(
        "evt_cluster_support",
        transit_body="Venus",
        natal_point="Mercury",
        aspect="sextile",
        mode="opening",
        house=3,
        felt="Bugün aynı konuşmada daha yumuşak bir ton da bulabilirsin.",
        guidance="Yumuşayan kapıyı kaçırma",
    )
    unrelated = _card(
        "evt_unrelated",
        transit_body="Jupiter",
        natal_point="Moon",
        aspect="trine",
        mode="flow",
        house=10,
        felt="Bugün iş tarafında akış daha rahat olabilir.",
    )

    out = build_daily_synthesis(
        daily_event_cards=[trigger],
        period_event_cards=[unrelated, support],
        period_core={"title": "Zihinsel Eşiğini Yeniden Ayarlıyorsun"},
        natal_snapshot={},
    )

    assert out["support_signal"]["event_id"] == "evt_cluster_support"
    assert "yumuşak bir ton" in out["body"].lower()
    assert out["planner_debug"]["support_resolution"]["source"] == "cluster_support_ids"


def test_daily_synthesis_headline_changes_when_support_or_mode_changes() -> None:
    trigger = _card(
        "evt_trigger",
        transit_body="Neptune",
        natal_point="Sun",
        aspect="square",
        mode="friction",
        house=1,
        felt="Bugün kendini net tutmak zorlaşabilir.",
        guidance="İlk tepkiyi yavaşlat",
    )
    support = _card(
        "evt_support",
        transit_body="Venus",
        natal_point="Sun",
        aspect="sextile",
        mode="opening",
        house=3,
        felt="Bugün bir konuşmada işleyen bir kapı da bulabilirsin.",
        guidance="Açılan cümleyi küçümseme",
    )

    pressure_only = build_daily_synthesis(
        daily_event_cards=[trigger],
        period_core={"title": "Kimliğini Yeniden Kuruyorsun"},
        natal_snapshot={},
    )
    mixed = build_daily_synthesis(
        daily_event_cards=[trigger],
        period_event_cards=[support],
        period_core={
            "title": "Kimliğini Yeniden Kuruyorsun",
            "featured_events": [trigger, support],
            "_period_story_debug": {
                "spine_event_id": "evt_trigger",
                "support_event_ids": ["evt_support"],
            },
        },
        natal_snapshot={},
    )

    assert pressure_only["narrative_mode"] == "pressure_dominant"
    assert mixed["narrative_mode"] == "mixed"
    assert pressure_only["headline"] != mixed["headline"]
    assert any(token in mixed["headline"].lower() for token in ("açıl", "kapı", "zorlasa"))
