from app.transit.narrative.chapter_role_engine import infer_chapter_role
from app.transit.narrative.event_feature_vector import build_event_feature_vector


def _event(
    event_id: str,
    *,
    transit_body: str = "Saturn",
    natal_point: str = "ASC",
    aspect: str = "square",
    bucket: str = "long",
    phase: str = "applying",
    orb_deg: float = 0.5,
    house: int = 10,
) -> dict:
    return {
        "event_id": event_id,
        "transit_body": transit_body,
        "natal_point": natal_point,
        "aspect": aspect,
        "bucket": bucket,
        "phase": phase,
        "orb_deg": orb_deg,
        "strength": 0.82,
        "houses": {"transit_in_natal_house": house, "natal_point_house": house},
        "ranking": {"tier": "main", "weight": 1.4, "exact_in_days": 0 if phase in {"exact", "exactish"} else 2},
        "timing": {
            "peak_date_utc": "2026-03-31T09:00:00+00:00",
            "entry_date_utc": "2026-03-29T09:00:00+00:00",
            "exit_date_utc": "2026-04-05T09:00:00+00:00",
        },
    }


def _card(event: dict) -> dict:
    house = event["houses"]["natal_point_house"]
    return {
        "event_id": event["event_id"],
        "transit_body": event["transit_body"],
        "natal_point": event["natal_point"],
        "aspect": event["aspect"],
        "bucket": event["bucket"],
        "phase": event["phase"],
        "derived_context": {"natal_target": {"house": house}},
        "scene": {"outcome_house": house, "start_house": house},
        "natal_promise": {"score": 0.73},
        "tags": {"exact_in_days": ((event.get("ranking") or {}).get("exact_in_days"))},
    }


def _preview(*, felt: str, why: str, guidance: str, house_touchpoint: str, tone_face: str = "growth") -> dict:
    return {
        "felt_line_tr": felt,
        "why_it_feels_this_way_tr": why,
        "guidance_micro_tr": guidance,
        "house_touchpoint_tr": house_touchpoint,
        "tone_face": tone_face,
    }


def test_feature_vector_exposes_strength_time_meaning_axes() -> None:
    event = _event("evt_feature")
    feature_vector = build_event_feature_vector(
        event,
        selected_date="2026-03-31",
        card=_card(event),
        event_v2_meta={
            "event_family": "station_event",
            "importance_tier": "high",
            "significance_score": 0.78,
            "lasting_change_score": 0.74,
            "chapter_opening": 0.66,
            "repeat_pass_count": 1,
            "is_structural": True,
        },
        preview=_preview(
            felt="İş tarafında baskı ile netlik aynı anda çalışabilir bugün.",
            why="Yön duygun görünür oldukça sorumluluk da ağırlaşır.",
            guidance="Tek karar kanalında kal.",
            house_touchpoint="yönün ve görünürlüğün",
        ),
    )

    assert feature_vector["strength"]["orb_proximity"] > 0.8
    assert feature_vector["time"]["is_peaking_today"] is True
    assert feature_vector["meaning"]["house_domain"] == "career"
    assert feature_vector["meaning"]["structurality"] > 0.7
    assert feature_vector["redundancy"]["cluster_key"] == "career|friction|saturn"


def test_chapter_role_prefers_builder_for_structural_long_event() -> None:
    event = _event("evt_builder", phase="applying", bucket="long")
    feature_vector = build_event_feature_vector(
        event,
        selected_date="2026-03-27",
        card=_card(event),
        event_v2_meta={
            "event_family": "aspect_event",
            "importance_tier": "high",
            "significance_score": 0.74,
            "lasting_change_score": 0.92,
            "chapter_opening": 0.12,
            "repeat_pass_count": 2,
            "is_structural": True,
        },
        preview=_preview(
            felt="Yön tarafında daha kalıcı bir ağırlık kuruluyor.",
            why="Aynı konuda tekrar tekrar ciddileşmen boşuna değil.",
            guidance="Yükü sisteme dağıt.",
            house_touchpoint="yönün ve görünürlüğün",
        ),
    )

    chapter_role = infer_chapter_role(event, features=feature_vector)

    assert chapter_role["role"] == "builder"
    assert chapter_role["scores"]["builder"] > chapter_role["scores"]["opener"]
