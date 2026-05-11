from types import SimpleNamespace

from app.api.routes import natal_interpretation as route_module
from app.astro_os.natal.contracts import (
    CanonicalNatalStateV1,
    ChartSpine,
    ChartSpineLine,
    ContradictionNode,
    NatalEvidence,
    NatalPromiseNode,
)
from app.astro_os.natal.meaning_graph import build_natal_meaning_graph


def _canonical_evidence(evidence_id: str, technical: str) -> NatalEvidence:
    return NatalEvidence(
        id=evidence_id,
        factor=technical,
        technical=technical,
        humanized=technical,
        layer="promise",
        role="support",
    )


def test_internal_natal_state_route_returns_partial_state_without_surface_branches(
    monkeypatch,
) -> None:
    sample_chart = {
        "birth_date": "1996-12-28",
        "birth_time": "07:10",
        "birth_place": "Istanbul",
        "planets": [],
        "aspects": [],
    }
    sample_request = route_module.NatalInterpretationRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul",
    )

    monkeypatch.setattr(route_module, "compute_natal_chart", lambda *args, **kwargs: sample_chart)
    monkeypatch.setattr(
        route_module,
        "NatalContext",
        SimpleNamespace(
            from_chart=lambda chart: SimpleNamespace(
                planets=[],
                aspects=[],
                chart_for_selection=chart,
            )
        ),
    )
    monkeypatch.setattr(route_module, "build_natal_graph", lambda **kwargs: {"importance": {}})
    monkeypatch.setattr(
        route_module,
        "build_natal_graph_v2",
        lambda chart, natal_graph=None: {"promise_vectors": {"identity": 0.1}},
    )
    monkeypatch.setattr(
        route_module,
        "build_natal_feature_graph",
        lambda **kwargs: {"dominant_planets": []},
    )
    monkeypatch.setattr(
        route_module,
        "build_primitives_v2",
        lambda *args, **kwargs: {"entries": []},
    )
    monkeypatch.setattr(
        route_module,
        "build_contradiction_signatures",
        lambda **kwargs: {"signatures": []},
    )
    monkeypatch.setattr(
        route_module,
        "build_master_natal_selector",
        lambda **kwargs: {"identity_spine": {}},
    )
    monkeypatch.setattr(
        route_module,
        "build_profile_narrative",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("profile branch should not be called")),
    )
    monkeypatch.setattr(
        route_module,
        "build_personality_imprint",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("personality imprint should not be called")),
    )

    payload = route_module.build_internal_natal_state(sample_request)

    assert payload["chart_id"].startswith("1996-12-28_07:10")
    assert payload["core_promises"] == []
    assert payload["character_patterns"] == []
    assert payload["contradictions"] == []
    assert payload["meaning_graph"]["version"] == "natal_meaning_graph_v1"
    assert payload["debug"]["legacy_sources_used"] == [
        "natal_graph",
        "natal_graph_v2",
        "feature_graph",
        "promise_vectors",
        "contradiction_signatures",
        "master_selector",
    ]


def test_internal_natal_compare_route_returns_comparison_payload(monkeypatch) -> None:
    sample_request = route_module.NatalInterpretationRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul",
    )
    sample_base_payload = {
        "metadata": {"chart_id": "chart_compare_1"},
        "chart_data": {
            "birth_date": "1996-12-28",
            "birth_time": "07:10",
            "birth_place": "Istanbul",
        },
        "personality_imprint": {
            "entries": [
                {
                    "label_tr": "Güneş 10. Ev",
                    "trait": "Yaptığın şeyin ciddiye alınmasını ve görünür karşılık bulmasını istersin.",
                }
            ]
        },
        "profile_narrative": {
            "profile_public": {
                "blocks": [
                    {
                        "headline": "Zihin tonu",
                        "body": "Düşünceleri yapılandırarak ifade etmeye eğilimli olabilirsin.",
                    }
                ]
            }
        },
        "sections_v2": [],
        "supporting_threads": [],
        "_natal_graph_v2": {
            "promise_vectors": {"mature_visibility": 0.61},
            "debug": {
                "vector_evidence": {
                    "mature_visibility": ["MC ruler carries visibility lesson"],
                }
            },
        },
        "_natal_feature_graph_v2": {"dominant_planets": []},
        "_contradiction_signatures_v1": {"signatures": []},
        "_master_selector_v1": {"work_visibility_line": {"line_id": "visibility_candidate"}},
    }

    monkeypatch.setattr(route_module, "_prepare_payload", lambda *args, **kwargs: sample_base_payload)

    payload = route_module.compare_internal_natal_state(sample_request)

    assert payload["canonical_state"]["chart_id"] == "chart_compare_1"
    assert payload["canonical_state"]["meaning_graph"]["version"] == "natal_meaning_graph_v1"
    assert payload["comparison"]["legacy_surface_counts"]["personality_imprint_entries"] == 1
    assert "phrase_rescue_candidates" in payload["comparison"]
    assert "semantic_loss_risks" in payload["comparison"]


def test_internal_natal_render_route_returns_state_derived_renders(monkeypatch) -> None:
    sample_chart = {
        "birth_date": "1996-12-28",
        "birth_time": "07:10",
        "birth_place": "Istanbul",
        "planets": [],
        "aspects": [],
    }
    sample_request = route_module.NatalInterpretationRequest(
        birth_date="1996-12-28",
        birth_time="07:10",
        birth_place="Istanbul",
    )
    monkeypatch.setattr(route_module, "compute_natal_chart", lambda *args, **kwargs: sample_chart)
    relationship = NatalPromiseNode(
        id="promise_build_safe_intimacy",
        domain="relationship",
        theme="safe intimacy through trust and depth",
        centrality="core",
        stability="lifelong",
        evidence=[_canonical_evidence("rel_1", "7th ruler in 8th"), _canonical_evidence("rel_2", "Moon in 8th")],
        psychological_pattern="Closeness is filtered through trust and depth.",
        potential="Durable intimacy.",
        growth_path="Let trust build gradually.",
    )
    work = NatalPromiseNode(
        id="promise_mature_visibility",
        domain="career_visibility",
        theme="maturing visibility and public presence",
        centrality="major",
        stability="lifelong",
        evidence=[_canonical_evidence("work_1", "MC ruler carries visibility lesson")],
        psychological_pattern="Visibility and legitimacy stay linked.",
        potential="Embodied public role.",
        growth_path="Practice measured visibility.",
    )
    contradiction = ContradictionNode(
        id="contradiction_closeness_vs_threshold",
        title="closeness with a high trust threshold",
        polarity_a="intimacy_depth",
        polarity_b="emotional_threshold",
        centrality="primary",
        evidence=[_canonical_evidence("con_1", "depth_intimacy"), _canonical_evidence("con_2", "thresholded_intimacy")],
        integration_path="Closeness grows through selective trust rather than instant access.",
    )
    state = CanonicalNatalStateV1(
        chart_id="1996-12-28_07:10_istanbul",
        core_promises=[relationship, work],
        contradictions=[contradiction],
        chart_spine=ChartSpine(
            relational_line=ChartSpineLine(
                key="relational_line",
                node_id=contradiction.id,
                title=contradiction.title,
                summary=contradiction.integration_path,
                evidence=contradiction.evidence,
                linked_node_ids=[contradiction.id],
            ),
            work_visibility_line=ChartSpineLine(
                key="work_visibility_line",
                node_id=work.id,
                title=work.theme,
                summary=work.growth_path,
                evidence=work.evidence,
                linked_node_ids=[work.id],
            ),
        ),
    )
    state.meaning_graph = build_natal_meaning_graph(state)

    monkeypatch.setattr(
        route_module,
        "build_canonical_natal_state_from_chart_data",
        lambda chart_data, metadata=None, include_debug=True: state,
    )
    monkeypatch.setattr(
        route_module,
        "build_profile_narrative",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("profile branch should not be called")),
    )
    monkeypatch.setattr(
        route_module,
        "build_personality_imprint",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("personality imprint should not be called")),
    )

    payload = route_module.render_internal_natal_state(sample_request)

    assert payload["canonical_state"]["chart_id"].startswith("1996-12-28_07:10")
    assert payload["canonical_state"]["meaning_graph"]["version"] == "natal_meaning_graph_v1"
    assert payload["compact_profile"]["relationship_pattern"]["node_id"] == "contradiction_closeness_vs_threshold"
    assert payload["compact_profile"]["work_visibility_pattern"]["node_id"] == "promise_mature_visibility"
    assert payload["section_profile"]["sections"][0]["key"] in {
        "core_architecture",
        "relationship_dynamics",
    }
