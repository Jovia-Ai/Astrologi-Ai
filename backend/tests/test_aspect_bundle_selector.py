from app.natal.narrative.aspect_bundle_selector import select_aspect_bundles


def test_select_aspect_bundles_prefers_recognizable_diverse_candidates() -> None:
    response = {
        "planets": [
            {"planet": "Moon", "house": 8, "sign": "Scorpio"},
            {"planet": "Saturn", "house": 4, "sign": "Aquarius"},
            {"planet": "Mercury", "house": 3, "sign": "Virgo"},
            {"planet": "Venus", "house": 7, "sign": "Pisces"},
            {"planet": "Ascendant", "house": 1, "sign": "Capricorn"},
        ],
        "aspects": [
            {"planet1": "Moon", "planet2": "Saturn", "aspect": "square", "orb": 0.8},
            {"planet1": "Mercury", "planet2": "Venus", "aspect": "trine", "orb": 1.2},
            {"planet1": "Ascendant", "planet2": "Moon", "aspect": "conjunction", "orb": 1.5},
        ],
        "expression_profile": {
            "domain_vectors": {
                "relationships": 0.82,
                "mind_communication": 0.76,
                "identity": 0.71,
                "intimacy_depth": 0.79,
            }
        },
    }

    out = select_aspect_bundles(response)
    bundles = out["selected_bundles"]

    assert out["max_primary_bundles"] == 3
    assert bundles
    assert len(bundles) <= 3
    bundle_types = {item["bundle_type"] for item in bundles}
    assert "emotional_regulation_bundle" in bundle_types
    assert "mental_style_bundle" in bundle_types or "relational_pattern_bundle" in bundle_types
    assert all(item["recognition_tags"] for item in bundles)
    assert all(item["gift_tags"] for item in bundles)
    assert all(item["reflex_tags"] for item in bundles)

