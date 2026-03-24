import sys
import types
import json
import re

from app.natal.natal_graph_v2 import build_natal_graph_v2
from app.synastry.activation_engine import overlay_domain_activation, synastry_hit_to_partner_activation


def _chart_a() -> dict:
    return {
        "planets": {
            "Sun": {"longitude": 276.75, "sign": "Capricorn", "house": 1},
            "Moon": {"longitude": 133.95, "sign": "Leo", "house": 8},
            "Mercury": {"longitude": 287.37, "sign": "Capricorn", "house": 1},
            "Venus": {"longitude": 253.71, "sign": "Sagittarius", "house": 12},
            "Mars": {"longitude": 177.93, "sign": "Virgo", "house": 9},
            "Jupiter": {"longitude": 294.30, "sign": "Capricorn", "house": 1},
            "Saturn": {"longitude": 1.16, "sign": "Aries", "house": 3},
            "Uranus": {"longitude": 303.06, "sign": "Aquarius", "house": 1},
            "Neptune": {"longitude": 296.69, "sign": "Capricorn", "house": 1},
            "Pluto": {"longitude": 244.26, "sign": "Sagittarius", "house": 11},
            "Node": {"longitude": 182.69, "sign": "Libra", "house": 9},
            "Lilith": {"longitude": 141.0, "sign": "Leo", "house": 8},
            "Chiron": {"longitude": 209.89, "sign": "Libra", "house": 10},
            "Fortune": {"longitude": 53.99, "sign": "Taurus", "house": 5},
        },
        "houses": {
            "1": 271.1868,
            "2": 310.2653,
            "3": 351.8247,
            "4": 25.2852,
            "5": 50.4481,
            "6": 71.1931,
            "7": 91.1868,
            "8": 130.2653,
            "9": 171.8247,
            "10": 205.2852,
            "11": 230.4481,
            "12": 251.1931,
        },
        "house_positions": {
            "1": {"sign": "Capricorn"},
            "2": {"sign": "Aquarius"},
            "3": {"sign": "Pisces"},
            "4": {"sign": "Aries"},
            "5": {"sign": "Taurus"},
            "6": {"sign": "Gemini"},
            "7": {"sign": "Cancer"},
            "8": {"sign": "Leo"},
            "9": {"sign": "Virgo"},
            "10": {"sign": "Libra"},
            "11": {"sign": "Scorpio"},
            "12": {"sign": "Sagittarius"},
        },
        "angles": {
            "ascendant": 271.1868,
            "midheaven": 205.2851,
            "ascendant_sign": "Capricorn",
            "midheaven_sign": "Libra",
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Saturn", "aspect": "square", "orb": 5.59},
            {"planet1": "Moon", "planet2": "Venus", "aspect": "trine", "orb": 0.24},
            {"planet1": "Mars", "planet2": "Saturn", "aspect": "opposition", "orb": 3.23},
            {"planet1": "Mars", "planet2": "Neptune", "aspect": "trine", "orb": 1.24},
            {"planet1": "Jupiter", "planet2": "Neptune", "aspect": "conjunction", "orb": 2.39},
            {"planet1": "Jupiter", "planet2": "Midheaven", "aspect": "square", "orb": 0.99},
            {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "square", "orb": 1.40},
        ],
    }


def _chart_b() -> dict:
    return {
        "planets": {
            "Sun": {"longitude": 169.22, "sign": "Virgo", "house": 12},
            "Moon": {"longitude": 67.6, "sign": "Gemini", "house": 9},
            "Mercury": {"longitude": 157.2, "sign": "Virgo", "house": 12},
            "Venus": {"longitude": 156.65, "sign": "Virgo", "house": 11},
            "Mars": {"longitude": 134.26, "sign": "Leo", "house": 11},
            "Jupiter": {"longitude": 353.58, "sign": "Pisces", "house": 6},
            "Saturn": {"longitude": 32.99, "sign": "Taurus", "house": 8},
            "Uranus": {"longitude": 309.34, "sign": "Aquarius", "house": 5},
            "Neptune": {"longitude": 299.61, "sign": "Capricorn", "house": 4},
            "Pluto": {"longitude": 245.5, "sign": "Sagittarius", "house": 3},
            "Node": {"longitude": 151.36, "sign": "Virgo", "house": 11},
            "Lilith": {"longitude": 210.19, "sign": "Scorpio", "house": 2},
            "Chiron": {"longitude": 225.61, "sign": "Scorpio", "house": 2},
            "Fortune": {"longitude": 81.5, "sign": "Gemini", "house": 9},
        },
        "houses": {
            "1": 183.1246,
            "2": 210.0251,
            "3": 240.5744,
            "4": 273.4906,
            "5": 306.3426,
            "6": 336.6655,
            "7": 3.1246,
            "8": 30.0251,
            "9": 60.5744,
            "10": 93.4906,
            "11": 126.3426,
            "12": 156.6655,
        },
        "house_positions": {
            "1": {"sign": "Libra"},
            "2": {"sign": "Scorpio"},
            "3": {"sign": "Sagittarius"},
            "4": {"sign": "Capricorn"},
            "5": {"sign": "Aquarius"},
            "6": {"sign": "Pisces"},
            "7": {"sign": "Aries"},
            "8": {"sign": "Taurus"},
            "9": {"sign": "Gemini"},
            "10": {"sign": "Cancer"},
            "11": {"sign": "Leo"},
            "12": {"sign": "Virgo"},
        },
        "angles": {
            "ascendant": 183.1246,
            "midheaven": 93.4906,
            "ascendant_sign": "Libra",
            "midheaven_sign": "Cancer",
        },
        "aspects": [
            {"planet1": "Sun", "planet2": "Mercury", "aspect": "conjunction", "orb": 0.20},
            {"planet1": "Venus", "planet2": "Mars", "aspect": "conjunction", "orb": 7.61},
            {"planet1": "Saturn", "planet2": "Neptune", "aspect": "trine", "orb": 3.38},
            {"planet1": "Neptune", "planet2": "Midheaven", "aspect": "opposition", "orb": 26.12},
        ],
    }


def _load_synastry_analysis_module():
    sys.modules["app.main"] = types.SimpleNamespace(app=None, create_app=None)
    fake_builder = types.ModuleType("app.astro.chart_engine.builder")
    fake_builder.build_natal_chart = lambda payload: payload["chart"]
    sys.modules["app.astro.chart_engine.builder"] = fake_builder
    sys.modules.pop("app.services.synastry_analysis", None)
    from app.services import synastry_analysis  # type: ignore

    return synastry_analysis


def _analyze_fixture_synastry(monkeypatch):
    synastry_analysis = _load_synastry_analysis_module()

    def fake_build_partner_chart(partner: dict) -> dict:
        return _chart_a() if partner.get("name") == "Person A" else _chart_b()

    monkeypatch.setattr(synastry_analysis, "_build_partner_chart", fake_build_partner_chart)
    return synastry_analysis.analyze_synastry(
        {
            "partner_a": {"name": "Person A"},
            "partner_b": {"name": "Person B"},
            "options": {"include_debug": True},
        }
    )


def test_overlay_domain_activation_maps_8th_to_intimacy() -> None:
    activation = overlay_domain_activation(8)

    assert activation["intimacy_depth"] > activation["relationships"]


def test_overlay_domain_activation_maps_12th_to_private_inner_world() -> None:
    activation = overlay_domain_activation(12)

    assert activation["private_inner_world"] > activation["home_roots"]
    assert "intimacy_depth" not in activation


def test_synastry_hit_to_partner_activation_uses_house_and_carryover() -> None:
    graph = build_natal_graph_v2(_chart_a())
    record = synastry_hit_to_partner_activation(
        None,
        {"body": "sun", "in_house": 8},
        graph,
    )

    assert record is not None
    assert "intimacy_depth" in record["domains"]
    assert len(record["domains"]) <= 2
    assert any("8th ruler" in item and "1st" in item for item in record["because"])


def test_synastry_hit_to_partner_activation_routes_12th_to_private_inner_world() -> None:
    graph = build_natal_graph_v2(_chart_b())
    record = synastry_hit_to_partner_activation(
        None,
        {"body": "sun", "in_house": 12},
        graph,
    )

    assert record is not None
    assert "private_inner_world" in record["domains"]
    assert len(record["domains"]) <= 2
    assert any("12th ruler" in item and "12th" in item for item in record["because"])


def test_analyze_synastry_adds_resonance_scores_non_breaking(monkeypatch) -> None:
    out = _analyze_fixture_synastry(monkeypatch)

    assert out["engine_version"] == "synastry_v1"
    assert out["public"]["scores"]["spark"] >= 0
    assert out["public"]["scores"] == out["public"]["contextual_scores"]
    assert out["public"]["raw_scores"]["depth"] < out["public"]["contextual_scores"]["depth"]
    assert out["public"]["raw_scores"]["bond"] < out["public"]["contextual_scores"]["bond"]
    assert "resonance_scores" in out["public"]
    assert "derived_context" in out["public"]
    assert "domain_rankings" in out["public"]
    assert "relational_modes" in out["public"]
    assert "narrative_ready" in out["public"]
    assert out["public"]["derived_context"]["partner_a_activated"]
    assert out["public"]["derived_context"]["meaning_summaries"]["partner_a"]
    assert out["public"]["derived_context"]["meaning_summaries"]["partner_b"]
    assert out["public"]["derived_context"]["meaning_summaries"]["relationship"]
    assert out["public"]["resonance_scores"]["partner_a"]["familiarity_resonance"] > 0
    assert out["public"]["resonance_scores"]["partner_a"]["promise_alignment"] > 0
    assert out["public"]["resonance_scores"]["partner_a"]["trigger_load"] > 0
    assert out["public"]["resonance_scores"]["partner_b"]["promise_alignment"] >= 35
    assert out["public"]["scores"]["depth"] >= 40
    assert out["public"]["scores"]["risk_index"] >= 20
    assert out["public"]["scores"]["bond"] >= 40
    assert out["public"]["scores"]["spark"] >= 50
    assert out["public"]["scores"]["depth"] - out["public"]["raw_scores"]["depth"] <= 46
    assert out["public"]["scores"]["risk_index"] - out["public"]["raw_scores"]["risk_index"] <= 35
    assert out["public"]["scores"]["bond"] - out["public"]["raw_scores"]["bond"] <= 32
    assert out["public"]["resonance_scores"]["relationship"]["asymmetry"] > 0
    assert all(row["score"] < 1.0 for row in out["public"]["domain_rankings"]["partner_a"][:3])
    assert all(row["score"] < 1.0 for row in out["public"]["domain_rankings"]["partner_b"][:3])
    assert "natal_graph_v2" in out["debug"]
    assert "resonance_hits" in out["debug"]
    assert "overlay_cluster_summary" in out["debug"]
    assert "activation_bundles" in out["debug"]
    assert "relationship_calibration" in out["debug"]
    assert "public_score_bridge_debug" in out["debug"]
    assert "promise_alignment_breakdown" in out["debug"]
    assert out["debug"]["overlay_cluster_summary"]["8th_personal_cluster_a"] >= 4
    assert 1 <= len(out["debug"]["activation_bundles"]["partner_a"]) <= 12
    assert 1 <= len(out["debug"]["activation_bundles"]["partner_b"]) <= 12
    assert out["debug"]["public_score_bridge_debug"]["bridge_contributors"]["depth"]
    assert out["debug"]["public_score_bridge_debug"]["bridge_contributors"]["risk_index"]
    assert out["debug"]["public_score_bridge_debug"]["bridge_contributors"]["bond"]
    assert out["debug"]["relationship_calibration"]["directional_asymmetry"] > 0
    assert out["public"]["narrative_ready"]["relationship_core"]["shared_theme"]
    assert out["public"]["narrative_ready"]["relationship_core"]["shared_theme_line"]
    assert out["public"]["narrative_ready"]["relationship_core"]["shared_support_line"]
    assert out["public"]["narrative_ready"]["relationship_core"]["shared_tension_line"]
    assert out["public"]["narrative_ready"]["partner_a_story"]["primary_domain"] == "intimacy_depth"
    assert out["public"]["narrative_ready"]["partner_a_story"]["summary_line"]
    assert out["public"]["narrative_ready"]["partner_b_story"]["primary_domain"] == "home_roots"
    assert out["public"]["narrative_ready"]["partner_b_story"]["summary_line"]
    assert out["public"]["narrative_ready"]["partner_a_story"]["primary_domain"] == out["public"]["domain_rankings"]["partner_a"][0]["domain"]
    assert out["public"]["narrative_ready"]["partner_b_story"]["primary_domain"] == out["public"]["domain_rankings"]["partner_b"][0]["domain"]
    assert out["public"]["narrative_ready"]["partner_b_story"]["secondary_domain"] == out["public"]["domain_rankings"]["partner_b"][1]["domain"]
    assert out["public"]["narrative_ready"]["partner_b_story"]["surface_domain"] == "home_roots"
    assert out["public"]["narrative_ready"]["partner_b_story"]["background_domain"] == "social_future"
    assert all("Partner A experiences" not in note for note in out["public"]["derived_context"]["asymmetry_notes"])
    assert out["public"]["drivers"]["depth"]
    assert out["public"]["drivers"]["risk_index"]
    assert out["debug"]["public_score_bridge_debug"]["canonical_scores"]["depth"] > out["public"]["raw_scores"]["depth"]
    assert out["debug"]["public_score_bridge_debug"]["canonical_scores"]["risk_index"] > out["public"]["raw_scores"]["risk_index"]
    assert out["debug"]["public_score_bridge_debug"]["bounded_bridge_applied"]["depth"] <= 0.08
    assert out["debug"]["public_score_bridge_debug"]["bounded_bridge_applied"]["bond"] <= 0.08
    assert out["debug"]["public_score_bridge_debug"]["bounded_bridge_applied"]["risk_index"] <= 0.06
    assert out["debug"]["public_score_bridge_debug"]["target_scores_before_shaping"]["depth"] >= out["public"]["scores"]["depth"] / 100
    assert out["debug"]["public_score_bridge_debug"]["spark_floor_applied"] >= 0.0
    debug_blob = json.dumps(
        {
            "activation_bundles": out["debug"]["activation_bundles"],
            "resonance_hits": out["debug"]["resonance_hits"][:40],
            "domain_rankings": out["debug"]["domain_rankings"],
        },
        ensure_ascii=False,
    )
    assert not re.search(r"\b1th\b", debug_blob)
    assert not re.search(r"\b2th\b", debug_blob)
    assert not re.search(r"\b3th\b", debug_blob)
    assert out["debug"]["public_score_bridge_debug"]["unscored_but_relevant_hits"] == []


def test_analyze_synastry_resonance_is_deterministic(monkeypatch) -> None:
    first = _analyze_fixture_synastry(monkeypatch)
    second = _analyze_fixture_synastry(monkeypatch)

    assert first == second


def test_activation_bundles_compact_directional_hits(monkeypatch) -> None:
    out = _analyze_fixture_synastry(monkeypatch)
    partner_a_kinds = {bundle["kind"] for bundle in out["debug"]["activation_bundles"]["partner_a"]}
    partner_b_kinds = {bundle["kind"] for bundle in out["debug"]["activation_bundles"]["partner_b"]}

    assert "8th_personal_cluster" in partner_a_kinds
    assert "roots_home_bundle" in partner_b_kinds
    assert "social_future_bundle" in partner_b_kinds
    assert "soft_attraction_bundle" not in partner_a_kinds
    assert out["public"]["narrative_ready"]["relationship_shape"]["asymmetry"] > 0


def test_activation_bundles_use_single_source_ownership(monkeypatch) -> None:
    out = _analyze_fixture_synastry(monkeypatch)

    for partner_key in ("partner_a", "partner_b"):
        seen_source_ids: set[str] = set()
        bundles = out["debug"]["activation_bundles"][partner_key]
        for bundle in bundles:
            source_ids = set(bundle.get("source_hit_ids") or [])
            assert bundle["count"] == bundle["unique_hit_count"] == len(source_ids)
            assert bundle["displayed_evidence_count"] <= 5
            assert len(bundle.get("evidence") or []) <= 5
            assert not (seen_source_ids & source_ids)
            seen_source_ids.update(source_ids)


def test_cluster_bundles_outweigh_support_bridges(monkeypatch) -> None:
    out = _analyze_fixture_synastry(monkeypatch)

    partner_a_bundles = {bundle["kind"]: bundle for bundle in out["debug"]["activation_bundles"]["partner_a"]}
    partner_b_bundles = {bundle["kind"]: bundle for bundle in out["debug"]["activation_bundles"]["partner_b"]}

    assert partner_a_bundles["8th_personal_cluster"]["score"] > partner_a_bundles["communication_bridge_bundle"]["score"]
    assert partner_b_bundles["roots_home_bundle"]["score"] > partner_b_bundles["communication_bridge_bundle"]["score"]
