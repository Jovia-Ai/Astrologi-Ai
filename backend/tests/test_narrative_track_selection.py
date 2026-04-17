from app.transit.narrative.astrolog_narrative_engine import (
    TRACK_IDS,
    infer_story_track_id,
)


# S0-3b: Period track seçim kurallarının regression + yeni house-based
# fallback'lerini doğrulayan unit testler. İçerik (S0-3a) için test_phrase_lib_tr.py'ye bakın.


def _card(**overrides):
    base = {
        "event_id": "evt_test",
        "transit_body": "Saturn",
        "aspect": "trine",
        "natal_point": "Sun",
        "houses": {},
    }
    base.update(overrides)
    return base


# ---------- TRACK_IDS coverage ----------

def test_track_ids_covers_nine_tracks_plus_default() -> None:
    expected = {
        "identity_spine",
        "method_shift_9_virgo",
        "network_transform_11",
        "mirror_axis_1_7",
        "resource_axis_2_8",
        "healing_axis_6_12",
        "creativity_5",
        "root_4",
        "dissolution_12",
        "default",
    }
    assert TRACK_IDS == expected


# ---------- Root causes priority 1 (regression) ----------

def test_root_causes_match_wins_over_body_rules() -> None:
    card = _card(event_id="evt_rc1", transit_body="Uranus")
    root_causes = [
        {"key": "resource_axis_2_8", "score": 0.91, "evidence": ["evt_rc1"]},
    ]
    # Uranus normalde method_shift_9_virgo döner ama root_cause eşleşmesi priority 1.
    assert infer_story_track_id(card, period_root_causes=root_causes) == "resource_axis_2_8"


def test_root_causes_unknown_key_is_ignored() -> None:
    card = _card(event_id="evt_rc2", transit_body="Uranus")
    root_causes = [
        {"key": "not_a_real_track", "score": 0.99, "evidence": ["evt_rc2"]},
    ]
    # Bilinmeyen key — body kuralına düşmeli (Uranus → method_shift).
    assert infer_story_track_id(card, period_root_causes=root_causes) == "method_shift_9_virgo"


# ---------- Mevcut 5 kural (regression) ----------

def test_dsc_target_returns_mirror() -> None:
    assert infer_story_track_id(_card(natal_point="DSC")) == "mirror_axis_1_7"


def test_neptune_asc_hard_returns_identity_spine() -> None:
    card = _card(transit_body="Neptune", aspect="square", natal_point="ASC")
    assert infer_story_track_id(card) == "identity_spine"


def test_neptune_mc_opposition_returns_mirror() -> None:
    card = _card(transit_body="Neptune", aspect="opposition", natal_point="MC")
    assert infer_story_track_id(card) == "mirror_axis_1_7"


def test_uranus_any_returns_method_shift() -> None:
    assert infer_story_track_id(_card(transit_body="Uranus", natal_point="Mars")) == "method_shift_9_virgo"


def test_pluto_body_returns_network_transform() -> None:
    assert infer_story_track_id(_card(transit_body="Pluto", natal_point="Venus")) == "network_transform_11"


def test_pluto_target_returns_network_transform() -> None:
    assert infer_story_track_id(_card(transit_body="Saturn", natal_point="PLUTO")) == "network_transform_11"


# ---------- Yeni 5 house-based kural ----------

def test_neptune_in_natal_house_12_returns_dissolution() -> None:
    card = _card(transit_body="Neptune", natal_point="Moon", houses={"transit_in_natal_house": 12})
    assert infer_story_track_id(card) == "dissolution_12"


def test_non_neptune_in_house_12_returns_healing_not_dissolution() -> None:
    # 12. ev ama Neptune değil → healing catch-all.
    card = _card(transit_body="Saturn", natal_point="Moon", houses={"transit_in_natal_house": 12})
    assert infer_story_track_id(card) == "healing_axis_6_12"


def test_house_6_returns_healing() -> None:
    card = _card(transit_body="Saturn", houses={"transit_in_natal_house": 6})
    assert infer_story_track_id(card) == "healing_axis_6_12"


def test_house_2_returns_resource() -> None:
    card = _card(transit_body="Saturn", houses={"transit_in_natal_house": 2})
    assert infer_story_track_id(card) == "resource_axis_2_8"


def test_house_8_returns_resource() -> None:
    card = _card(transit_body="Saturn", houses={"transit_in_natal_house": 8})
    assert infer_story_track_id(card) == "resource_axis_2_8"


def test_house_5_returns_creativity() -> None:
    card = _card(transit_body="Saturn", houses={"transit_in_natal_house": 5})
    assert infer_story_track_id(card) == "creativity_5"


def test_house_4_returns_root() -> None:
    card = _card(transit_body="Saturn", houses={"transit_in_natal_house": 4})
    assert infer_story_track_id(card) == "root_4"


# ---------- Priority: mevcut body kuralları yeni house kurallarından önce ----------

def test_uranus_in_house_5_still_returns_method_shift_not_creativity() -> None:
    # Uranus body kuralı house-based kurallardan önce; creativity_5'e düşmemeli.
    card = _card(transit_body="Uranus", houses={"transit_in_natal_house": 5})
    assert infer_story_track_id(card) == "method_shift_9_virgo"


def test_pluto_in_house_4_still_returns_network_transform_not_root() -> None:
    card = _card(transit_body="Pluto", houses={"transit_in_natal_house": 4})
    assert infer_story_track_id(card) == "network_transform_11"


# ---------- Default fallback ----------

def test_house_1_returns_default() -> None:
    card = _card(transit_body="Saturn", houses={"transit_in_natal_house": 1})
    assert infer_story_track_id(card) == "default"


def test_missing_houses_returns_default() -> None:
    card = _card(transit_body="Saturn", houses=None)
    assert infer_story_track_id(card) == "default"


def test_no_matching_rule_returns_default() -> None:
    # Body + target + houses hiçbir kurala uymuyor → default.
    card = _card(transit_body="Saturn", natal_point="Mercury", houses={"transit_in_natal_house": 10})
    assert infer_story_track_id(card) == "default"
