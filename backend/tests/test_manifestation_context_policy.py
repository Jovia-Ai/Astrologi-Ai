from app.transit.narrative.manifestation_context_policy import (
    HOUSE_LIFE_SCENES,
    build_manifestation_context,
)


def _context(*, event_id: str, spine_line: str, event_nature: str, house: int, natal_point: str = "Venus", chapter_role: str = "builder") -> dict:
    return build_manifestation_context(
        matched_events=[
            {
                "event_id": event_id,
                "transit_body": "Saturn",
                "aspect": "conjunction",
                "natal_point": natal_point,
                "houses": {"transit_in_natal_house": house, "natal_point_house": house},
            }
        ],
        spine_line=spine_line,
        event_nature=event_nature,
        chapter_role=chapter_role,
    )


def test_each_house_has_at_least_three_life_scene_variants() -> None:
    for house, variants in HOUSE_LIFE_SCENES.items():
        assert house in range(1, 13)
        assert len(variants) >= 3


def test_manifestation_context_is_deterministic_for_same_inputs() -> None:
    first = _context(event_id="evt_same", spine_line="work_visibility_line", event_nature="responsibility", house=6)
    second = _context(event_id="evt_same", spine_line="work_visibility_line", event_nature="responsibility", house=6)

    assert first == second


def test_same_spine_and_event_with_different_houses_change_context_seed() -> None:
    sixth = _context(event_id="evt_work_6", spine_line="work_visibility_line", event_nature="responsibility", house=6)
    tenth = _context(event_id="evt_work_10", spine_line="work_visibility_line", event_nature="responsibility", house=10, natal_point="MC")

    assert sixth["primary_house"] == 6
    assert tenth["primary_house"] == 10
    assert sixth["life_scene"] != tenth["life_scene"]
    assert sixth["context_seed"] != tenth["context_seed"]


def test_relational_saturn_uses_communication_scene_for_third_house() -> None:
    context = _context(event_id="evt_rel_3", spine_line="relational_line", event_nature="boundary", house=3)

    assert context["source"] == "event_house"
    assert context["life_scene"] in HOUSE_LIFE_SCENES[3]


def test_relational_saturn_uses_relationship_scene_for_seventh_house() -> None:
    context = _context(event_id="evt_rel_7", spine_line="relational_line", event_nature="boundary", house=7)

    assert context["source"] == "event_house"
    assert context["life_scene"] in HOUSE_LIFE_SCENES[7]


def test_shadow_neptune_twelfth_house_strengthens_release_context() -> None:
    context = build_manifestation_context(
        matched_events=[
            {
                "event_id": "evt_shadow_12",
                "transit_body": "Neptune",
                "aspect": "square",
                "natal_point": "ASC",
                "houses": {"transit_in_natal_house": 12, "natal_point_house": 1},
            }
        ],
        spine_line="shadow_protection_line",
        event_nature="dissolution",
        chapter_role="release",
    )

    assert context["life_scene"] in HOUSE_LIFE_SCENES[12]
    assert context["release_strengthened"] is True


def test_context_seed_does_not_leak_technical_astrology_terms() -> None:
    context = _context(event_id="evt_clean", spine_line="relational_line", event_nature="boundary", house=3)
    lowered = f"{context['life_scene']} {context['context_seed']}".lower()

    for token in ("3. ev", "6. ev", "10. ev", "transit", "açı", "square", "conjunction"):
        assert token not in lowered
