import pytest

from app.transit.narrative.period_voice_policy import build_period_voice_policy


def _policy(
    spine_line: str,
    body: str,
    *,
    aspect: str = "conjunction",
    natal_point: str = "Moon",
    chapter_role: str = "builder",
    recent_rhetorical_frames: list[str] | None = None,
    recent_valence_modes: list[str] | None = None,
) -> dict:
    return build_period_voice_policy(
        canonical_period_spine={
            "spine_lines": [spine_line],
            "target_node_id": f"node_{spine_line}",
            "matched_event_ids": [f"evt_{body.lower()}"],
        },
        matched_events=[
            {
                "event_id": f"evt_{body.lower()}",
                "transit_body": body,
                "aspect": aspect,
                "natal_point": natal_point,
            }
        ],
        chapter_role=chapter_role,
        canonical_backing_node_ids=[f"node_{spine_line}"],
        recent_rhetorical_frames=recent_rhetorical_frames,
        recent_valence_modes=recent_valence_modes,
    )


@pytest.mark.parametrize(
    ("spine_line", "body", "expected_nature", "expected_seed_prefix"),
    [
        ("relational_line", "Saturn", "boundary", "relational_boundary"),
        ("relational_line", "Venus", "closeness", "relational_closeness"),
        ("relational_line", "Moon", "closeness", "relational_closeness"),
        ("work_visibility_line", "Pluto", "control", "work_visibility_control"),
        ("shadow_protection_line", "Neptune", "dissolution", "shadow_protection_dissolution"),
        ("growth_integration_line", "Uranus", "change", "growth_integration_change"),
        ("emotional_regulation_line", "Moon", "regulation", "emotional_regulation_regulation"),
        ("primary_identity_line", "Sun", "courage", "primary_identity_courage"),
        ("primary_identity_line", "Mars", "courage", "primary_identity_courage"),
        ("primary_identity_line", "Jupiter", "courage", "primary_identity_courage"),
    ],
)
def test_fixture_backed_matrix_targets_are_exact_matches(
    spine_line: str,
    body: str,
    expected_nature: str,
    expected_seed_prefix: str,
) -> None:
    policy = _policy(spine_line, body)

    assert policy["mechanism_lens"] == f"{spine_line}.{expected_nature}"
    assert policy["psychological_process"] == f"{expected_seed_prefix}_process"
    assert policy["debug"]["event_nature"] == expected_nature
    assert policy["debug"]["policy_match"]["level"] == "exact"
    assert policy["debug"]["policy_match"]["seed_key"] == f"{spine_line}.{expected_nature}"


@pytest.mark.parametrize(
    ("spine_line", "body", "expected_intent", "expected_frames"),
    [
        ("relational_line", "Saturn", "trust_calibration", {"calibration", "mirror"}),
        ("work_visibility_line", "Saturn", "responsibility_selection", {"sorting", "threshold"}),
        ("shadow_protection_line", "Neptune", "softening", {"reframe", "naked"}),
        ("primary_identity_line", "Mars", "activation", {"threshold", "embodiment"}),
    ],
)
def test_fixture_backed_matrix_exposes_rhetorical_frames(
    spine_line: str,
    body: str,
    expected_intent: str,
    expected_frames: set[str],
) -> None:
    policy = _policy(spine_line, body)

    assert policy["meaning_intent"] == expected_intent
    assert policy["rhetorical_frame"] in expected_frames
    assert policy["debug"]["match_level"] == policy["debug"]["policy_match"]["level"]


def test_policy_falls_back_to_spine_line_generic_before_event_nature_generic() -> None:
    policy = _policy("relational_line", "Mercury", aspect="trine")

    assert policy["mechanism_lens"] == "relational_line.clarity"
    assert policy["psychological_process"] == "relational_default_process"
    assert policy["debug"]["policy_match"]["level"] == "spine_line_generic"
    assert policy["debug"]["policy_match"]["seed_key"] == "relational_line.default"


def test_policy_falls_back_to_event_nature_generic_for_unknown_spine_line() -> None:
    policy = _policy("unknown_line", "Pluto", aspect="square")

    assert policy["mechanism_lens"] == "unknown_line.control"
    assert policy["psychological_process"] == "generic_control_process"
    assert policy["debug"]["policy_match"]["level"] == "event_nature_generic"
    assert policy["debug"]["policy_match"]["seed_key"] == "*.control"


def test_policy_exposes_legacy_untouched_match_level_when_matrix_has_no_seed() -> None:
    policy = _policy("unknown_line", "Chiron", aspect="trine")

    assert policy["debug"]["event_nature"] == "clarity"
    assert policy["debug"]["policy_match"]["level"] == "legacy_untouched"
    assert "psychological_process" not in policy
    assert policy["reason_line_allowed"] is False


@pytest.mark.parametrize(
    ("spine_line", "body", "natal_point", "aspect", "chapter_role", "expected_valence", "expected_intensity"),
    [
        ("work_visibility_line", "Mars", "Saturn", "square", "builder", "tension", "dense"),
        ("relational_line", "Venus", "Jupiter", "square", "builder", "integration", "dense"),
        ("primary_identity_line", "Sun", "Moon", "square", "builder", "integration", "dense"),
        ("primary_identity_line", "Mars", "Pluto", "trine", "peak", "momentum", "dense"),
        ("work_visibility_line", "Saturn", "Mars", "sextile", "builder", "maturation", "medium"),
        ("shadow_protection_line", "Neptune", "ASC", "sextile", "release", "release", "light"),
        ("work_visibility_line", "Sun", "MC", "trine", "peak", "recognition", "light"),
    ],
)
def test_all_seven_valence_modes_and_three_intensity_modes_are_reachable(
    spine_line: str,
    body: str,
    natal_point: str,
    aspect: str,
    chapter_role: str,
    expected_valence: str,
    expected_intensity: str,
) -> None:
    policy = _policy(
        spine_line,
        body,
        aspect=aspect,
        natal_point=natal_point,
        chapter_role=chapter_role,
    )

    assert policy["valence_mode"] == expected_valence
    assert policy["intensity_mode"] == expected_intensity
    assert policy["debug"]["valence_debug"]["pair_class"]


def test_same_aspect_different_pair_changes_valence() -> None:
    mars_saturn = _policy("work_visibility_line", "Mars", aspect="square", natal_point="Saturn")
    venus_jupiter = _policy("relational_line", "Venus", aspect="square", natal_point="Jupiter")

    assert mars_saturn["intensity_mode"] == venus_jupiter["intensity_mode"] == "dense"
    assert mars_saturn["valence_mode"] == "tension"
    assert venus_jupiter["valence_mode"] == "integration"


def test_unknown_pair_fallback_is_deterministic_and_populates_debug() -> None:
    a = _policy("unknown_line", "Chiron", aspect="sextile", natal_point="Ceres")
    b = _policy("unknown_line", "Chiron", aspect="sextile", natal_point="Ceres")

    assert a["valence_mode"] == b["valence_mode"] == "integration"
    assert a["intensity_mode"] == b["intensity_mode"] == "medium"
    assert a["valence_debug"]["fallback_used"] is True
    assert a["debug"]["valence_debug"]["pair_class"] == "unclassified"


def test_valence_rotation_does_not_conflict_with_rhetorical_frame_rotation() -> None:
    policy = _policy(
        "work_visibility_line",
        "Sun",
        aspect="trine",
        natal_point="MC",
        chapter_role="peak",
        recent_rhetorical_frames=["threshold"],
        recent_valence_modes=["recognition"],
    )

    assert policy["rhetorical_frame"] == "reframe"
    assert policy["debug"]["frame_debug"]["rotation_applied"] is True
    assert policy["valence_mode"] == "opening"
    assert policy["valence_debug"]["rotation_applied"] is True
