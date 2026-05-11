from app.astro_os.natal.contracts import (
    CanonicalNatalStateV1,
    ChartSpine,
    ChartSpineLine,
    ContradictionNode,
    NatalEvidence,
    NatalPromiseNode,
)
from app.astro_os.natal.rendering import render_compact_profile, render_section_profile


def _evidence(evidence_id: str, technical: str) -> NatalEvidence:
    return NatalEvidence(
        id=evidence_id,
        factor=technical,
        technical=technical,
        humanized=technical,
        layer="promise",
        role="support",
    )


def test_compact_renderer_only_renders_claims_with_evidence() -> None:
    state = CanonicalNatalStateV1(
        chart_id="chart_emptyish",
        core_promises=[
            NatalPromiseNode(
                id="promise_identity",
                domain="identity",
                theme="embodying originality without fragmentation",
                centrality="core",
                stability="lifelong",
                evidence=[],
                psychological_pattern="Difference wants embodiment.",
                potential="Stable individuality.",
                growth_path="Own distinctiveness steadily.",
            )
        ],
        chart_spine=ChartSpine(
            primary_identity_line=ChartSpineLine(
                key="primary_identity_line",
                node_id="promise_identity",
                title="identity",
                summary="identity summary",
                evidence=[],
            )
        ),
    )

    compact = render_compact_profile(state)
    sections = render_section_profile(state)

    assert compact.opening is None
    assert compact.core_pattern is None
    assert compact.filled_slots == []
    assert sections.sections == []


def test_renderers_build_outputs_from_canonical_state_only() -> None:
    identity = NatalPromiseNode(
        id="promise_embody_originality",
        domain="identity",
        theme="embodying originality without fragmentation",
        centrality="major",
        stability="lifelong",
        evidence=[_evidence("id_1", "Uranus tied to Ascendant"), _evidence("id_2", "identity motif")],
        psychological_pattern="Difference wants to become lived identity.",
        potential="Stable distinctiveness.",
        growth_path="Let originality become embodied character.",
    )
    relationship = NatalPromiseNode(
        id="promise_build_safe_intimacy",
        domain="relationship",
        theme="safe intimacy through trust and depth",
        centrality="core",
        stability="lifelong",
        evidence=[_evidence("rel_1", "7th ruler in 8th"), _evidence("rel_2", "Moon in 8th")],
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
        integration_path="Closeness grows through selective trust rather than instant access.",
    )
    state = CanonicalNatalStateV1(
        chart_id="chart_1",
        core_promises=[relationship, identity, work],
        contradictions=[contradiction],
        chart_spine=ChartSpine(
            primary_identity_line=ChartSpineLine(
                key="primary_identity_line",
                node_id=identity.id,
                title=identity.theme,
                summary=identity.growth_path,
                evidence=identity.evidence,
                linked_node_ids=[identity.id],
            ),
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
            shadow_protection_line=ChartSpineLine(
                key="shadow_protection_line",
                node_id=contradiction.id,
                title=contradiction.title,
                summary=contradiction.integration_path,
                evidence=contradiction.evidence,
                linked_node_ids=[contradiction.id],
            ),
            growth_integration_line=ChartSpineLine(
                key="growth_integration_line",
                node_id=identity.id,
                title=identity.theme,
                summary=identity.growth_path,
                evidence=identity.evidence,
                linked_node_ids=[identity.id],
            ),
        ),
    )

    compact = render_compact_profile(state)
    sections = render_section_profile(state)

    assert compact.opening is not None
    assert compact.opening.node_id == identity.id
    assert compact.relationship_pattern is not None
    assert compact.relationship_pattern.node_id == contradiction.id
    assert compact.work_visibility_pattern is not None
    assert compact.work_visibility_pattern.node_id == work.id
    assert compact.shadow_growth is not None
    assert compact.shadow_growth.node_id == contradiction.id
    assert compact.integration is not None
    assert compact.integration.node_id == identity.id
    assert "Uranus tied to Ascendant" in compact.opening.evidence_refs

    section_keys = [section.key for section in sections.sections]
    assert section_keys == [
        "core_architecture",
        "relationship_dynamics",
        "work_and_visibility",
        "shadow_and_growth",
    ]
    assert identity.id in sections.sections[0].node_ids
    assert contradiction.id in sections.sections[1].node_ids
