from app.astro_os.natal.contracts import (
    CanonicalNatalStateV1,
    ChartSpine,
    ChartSpineLine,
    ContradictionNode,
    NatalEvidence,
    NatalPromiseNode,
)
from app.astro_os.natal.meaning_graph import build_natal_meaning_graph
from app.transit.narrative.canonical_natal_activation import build_transit_natal_activation_context


def _evidence(evidence_id: str, technical: str) -> NatalEvidence:
    return NatalEvidence(
        id=evidence_id,
        factor=technical,
        technical=technical,
        humanized=technical,
        layer="promise",
        role="support",
    )


def _state() -> CanonicalNatalStateV1:
    relationship = NatalPromiseNode(
        id="promise_build_safe_intimacy",
        domain="relationship",
        theme="safe intimacy through trust and depth",
        centrality="core",
        stability="lifelong",
        evidence=[_evidence("rel_1", "7th ruler in 8th"), _evidence("rel_2", "Moon in 8th")],
        psychological_pattern="Closeness filters through trust.",
        potential="Durable intimacy.",
        growth_path="Let trust build gradually.",
    )
    work = NatalPromiseNode(
        id="promise_mature_visibility",
        domain="career_visibility",
        theme="maturing visibility and public presence",
        centrality="major",
        stability="lifelong",
        evidence=[_evidence("work_1", "MC ruler carries visibility lesson")],
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
        evidence=[_evidence("con_1", "depth_intimacy"), _evidence("con_2", "thresholded_intimacy")],
        integration_path="Closeness grows through selective trust.",
    )
    state = CanonicalNatalStateV1(
        chart_id="chart_1",
        core_promises=[relationship, work],
        contradictions=[contradiction],
        chart_spine=ChartSpine(
            relational_line=ChartSpineLine(
                key="relational_line",
                node_id=contradiction.id,
                title=contradiction.title,
                summary=contradiction.integration_path,
                evidence=contradiction.evidence,
            ),
            work_visibility_line=ChartSpineLine(
                key="work_visibility_line",
                node_id=work.id,
                title=work.theme,
                summary=work.growth_path,
                evidence=work.evidence,
            ),
        ),
    )
    state.meaning_graph = build_natal_meaning_graph(state)
    return state


def test_transit_activation_context_matches_events_to_hooks() -> None:
    state = _state()
    context = build_transit_natal_activation_context(
        canonical_state=state,
        period_core={"title": "Core"},
        daily_event_cards=[
            {
                "event_id": "evt_daily_rel",
                "tags": {"domain": "relationships"},
                "scene": {"start_house": 7, "outcome_house": 8},
            }
        ],
        period_event_cards=[
            {
                "event_id": "evt_period_work",
                "tags": {"domain": "career"},
                "scene": {"start_house": 10, "outcome_house": 10},
            }
        ],
    )

    assert context["graph_version"] == "natal_meaning_graph_v1"
    assert context["daily_selection"]["matched_event_ids"] == ["evt_daily_rel"]
    assert context["period_core"]["matched_event_ids"] == ["evt_period_work"]
    assert "hook:contradiction_closeness_vs_threshold" in context["daily_selection"]["top_hook_ids"]
    assert "hook:promise_mature_visibility" in context["period_core"]["top_hook_ids"]
