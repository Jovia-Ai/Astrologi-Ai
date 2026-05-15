from __future__ import annotations

import copy
import dataclasses
import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Sequence


ClusterRole = Literal["primary_anchor", "secondary_anchor", "modifier"]
SurfaceRole = Literal["public_main", "public_support", "detail", "debug_only"]
FocusTier = Literal["strong", "medium_strong", "supporting", "detail_only"]

CLUSTER_PLAN_VERSION = "natal_promise_cluster_plan_v1"
_ENABLED_VALUES = {"1", "true", "yes", "on"}
DEFAULT_EXPLICIT_ANCHOR_BUDGET = 2
PUBLIC_MAIN_MAX = 7
DEFAULT_PUBLIC_MAIN_MIN = 5
DEFAULT_PUBLIC_MAIN_TARGET = 6
DEFAULT_DETAIL_TARGET = 10


@dataclass
class DomainFocusScoreV1:
    domain: str
    score: float
    tier: FocusTier
    packet_ids: list[str] = field(default_factory=list)
    evidence_summary: list[str] = field(default_factory=list)
    scoring_breakdown: dict[str, float] = field(default_factory=dict)


@dataclass
class ClusterPacketMemberV1:
    packet_id: str
    cluster_role: ClusterRole
    contribution_type: str
    source_type: str = ""
    reuse_anchor_ids: list[str] = field(default_factory=list)
    explicit_anchor_allowed: bool = True
    reason: str = ""
    subtype: str = ""


@dataclass
class PacketSuppressionStateV1:
    packet_id: str
    suppressed_from_public_main: bool
    keep_for: list[str] = field(default_factory=list)
    reason: str = ""
    superseded_by_cluster_id: str | None = None
    superseded_by_packet_id: str | None = None


@dataclass
class ClusterAnchorUsageV1:
    anchor_id: str
    packet_ids: list[str] = field(default_factory=list)
    cluster_ids: list[str] = field(default_factory=list)
    public_main_explicit_uses: int = 0
    explicit_use_budget: int = DEFAULT_EXPLICIT_ANCHOR_BUDGET
    chart_defining_override: bool = False


@dataclass
class NatalPromiseClusterV1:
    id: str
    domain: str
    domain_family: str
    cluster_label: str
    source_type: str
    cluster_strength: float
    public_card_priority: float
    focus_tier: FocusTier
    target_surface_role: SurfaceRole
    main_packet_id: str
    packet_members: list[ClusterPacketMemberV1] = field(default_factory=list)
    shared_themes: list[str] = field(default_factory=list)
    distinct_lived_scene: str = ""
    promise_types: list[str] = field(default_factory=list)
    technical_anchor_ids: list[str] = field(default_factory=list)
    dedupe_fingerprint: str = ""
    allowed_public_cards: int = 1
    allowed_detail_cards: int = 2
    selection_notes: list[str] = field(default_factory=list)
    scoring_breakdown: dict[str, float] = field(default_factory=dict)
    subtypes: list[str] = field(default_factory=list)


@dataclass
class ClusterSurfacePlanV1:
    public_main_cluster_ids: list[str] = field(default_factory=list)
    public_support_cluster_ids: list[str] = field(default_factory=list)
    detail_cluster_ids: list[str] = field(default_factory=list)
    debug_packet_ids: list[str] = field(default_factory=list)


@dataclass
class NatalPromiseClusterPlanV1:
    version: str
    source_packet_version: str
    locale: str
    focus_map: list[DomainFocusScoreV1] = field(default_factory=list)
    clusters: list[NatalPromiseClusterV1] = field(default_factory=list)
    suppressed_packets: list[PacketSuppressionStateV1] = field(default_factory=list)
    anchor_usage: list[ClusterAnchorUsageV1] = field(default_factory=list)
    surface_plan: ClusterSurfacePlanV1 = field(default_factory=ClusterSurfacePlanV1)
    candidate_packets: list[dict[str, Any]] = field(default_factory=list)
    candidate_packet_count: int = 0
    public_main_card_count: int = 0
    detail_card_count: int = 0
    meta: dict[str, Any] = field(default_factory=dict)


def build_natal_promise_cluster_plan_v1(
    candidate_packets: Sequence[Mapping[str, Any]] | None,
    *,
    locale: str = "tr",
) -> dict[str, Any]:
    packets = [dict(item) for item in candidate_packets or [] if isinstance(item, Mapping)]
    normalized = [_normalize_packet(packet) for packet in packets if str(packet.get("id") or "").strip()]
    # Adana audit §5 (aux anchor-bleed fix): packets whose ``meta`` carries the
    # ``aux_should_suppress_from_public`` flag had their seed-inherited anchors
    # / body snippets scrubbed by the packet-build domain filter and ended up
    # empty. Pull them out of the clustering pool so they never reach
    # public_main / public_support / detail. They remain in the plan's
    # ``debug_packet_ids`` and stay available for transit activation.
    eligible: list[dict[str, Any]] = []
    composed_candidates_pre: list[dict[str, Any]] = []
    suppressed_aux_pre: list[PacketSuppressionStateV1] = []
    for packet in normalized:
        meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
        source_type = str(packet.get("source_type") or meta.get("source_type") or "").strip()
        if isinstance(meta, Mapping) and bool(meta.get("non_public_discovery")):
            if source_type == "composed_semantic":
                composed_candidates_pre.append(packet)
                continue
            suppressed_aux_pre.append(
                PacketSuppressionStateV1(
                    packet_id=str(packet.get("id") or "").strip(),
                    suppressed_from_public_main=True,
                    keep_for=["debug", "transit_activation"],
                    reason="v0.6 discovery candidate is debug-only until a public-quality archetype exists",
                )
            )
            continue
        if isinstance(meta, Mapping) and bool(meta.get("aux_should_suppress_from_public")):
            suppressed_aux_pre.append(
                PacketSuppressionStateV1(
                    packet_id=str(packet.get("id") or "").strip(),
                    suppressed_from_public_main=True,
                    keep_for=["debug", "transit_activation"],
                    reason="aux variant left without in-domain anchors after cross-domain bleed filter",
                )
            )
            continue
        if packet.get("chart_facts_match") is False:
            suppressed_aux_pre.append(
                PacketSuppressionStateV1(
                    packet_id=str(packet.get("id") or "").strip(),
                    suppressed_from_public_main=True,
                    keep_for=["debug", "transit_activation"],
                    reason="packet encodes chart facts that do not match this chart",
                )
            )
            continue
        eligible.append(packet)
    normalized = eligible
    focus_map = _build_focus_map(normalized)
    clusters = _build_primary_clusters(normalized, focus_map)
    _add_cross_domain_memberships(clusters=clusters, packets=normalized, focus_map=focus_map)
    _finalize_cluster_roles_and_mains(clusters=clusters, focus_map=focus_map)
    anchor_usage = _build_anchor_usage(clusters)
    surface_plan, suppressed = _build_surface_plan(
        clusters=clusters,
        focus_map=focus_map,
        anchor_usage=anchor_usage,
        packets=normalized,
    )
    composed_suppressions = _build_composed_candidate_rollout_suppressions(
        candidate_packets=composed_candidates_pre,
        clusters=clusters,
        surface_plan=surface_plan,
    )
    # Merge the pre-clustering aux suppressions in front of cluster-derived
    # ones; ensure their ids are still listed in ``debug_packet_ids`` so the
    # transit-activation pipeline can still discover them.
    suppressed = [*composed_suppressions, *suppressed_aux_pre, *suppressed]
    aux_suppress_ids = {
        item.packet_id
        for item in [*composed_suppressions, *suppressed_aux_pre]
        if item.packet_id
    }
    if aux_suppress_ids:
        existing_debug = set(surface_plan.debug_packet_ids)
        surface_plan.debug_packet_ids = sorted(existing_debug | aux_suppress_ids)
    plan = NatalPromiseClusterPlanV1(
        version=CLUSTER_PLAN_VERSION,
        source_packet_version=str((packets[0].get("meta") or {}).get("packet_version") or "natal_promise_packets_v1") if packets else "natal_promise_packets_v1",
        locale=str(locale or "tr"),
        focus_map=focus_map,
        clusters=clusters,
        suppressed_packets=suppressed,
        anchor_usage=anchor_usage,
        surface_plan=surface_plan,
        candidate_packets=[copy.deepcopy(packet) for packet in packets],
        candidate_packet_count=len(packets),
        public_main_card_count=len(surface_plan.public_main_cluster_ids),
        detail_card_count=len(surface_plan.detail_cluster_ids),
        meta={
            "public_main_hard_max": PUBLIC_MAIN_MAX,
            "public_main_default_min": DEFAULT_PUBLIC_MAIN_MIN,
            "detail_default_target": DEFAULT_DETAIL_TARGET,
            "explicit_anchor_budget": DEFAULT_EXPLICIT_ANCHOR_BUDGET,
            **_build_audit_metrics_and_warnings(
                candidate_packets=packets,
                clusters=clusters,
                surface_plan=surface_plan,
                suppressed_packets=suppressed,
            ),
        },
    )
    return _to_dict(plan)


def _to_dict(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {key: _to_dict(item) for key, item in dataclasses.asdict(value).items()}
    if isinstance(value, list):
        return [_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: _to_dict(item) for key, item in value.items()}
    return value


def _env_enabled(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in _ENABLED_VALUES


def _build_composed_candidate_rollout_suppressions(
    *,
    candidate_packets: Sequence[Mapping[str, Any]],
    clusters: Sequence[NatalPromiseClusterV1],
    surface_plan: ClusterSurfacePlanV1,
) -> list[PacketSuppressionStateV1]:
    cluster_lookup = {cluster.id: cluster for cluster in clusters}
    public_main_clusters = [
        cluster_lookup[cluster_id]
        for cluster_id in surface_plan.public_main_cluster_ids
        if cluster_lookup.get(cluster_id) is not None
    ]
    suppressions: list[PacketSuppressionStateV1] = []
    for packet in candidate_packets:
        packet_id = str(packet.get("id") or "").strip()
        if not packet_id:
            continue
        if _public_voice_detail_rollout_active_for_packet(
            packet=packet,
            public_main_clusters=public_main_clusters,
        ):
            suppressions.append(
                PacketSuppressionStateV1(
                    packet_id=packet_id,
                    suppressed_from_public_main=True,
                    keep_for=["detail", "debug"],
                    reason="v0.9a.1 public_voice composed semantic candidate is detail-only while public_support/public_main remain disabled",
                )
            )
            continue
        suppressions.append(
            PacketSuppressionStateV1(
                packet_id=packet_id,
                suppressed_from_public_main=True,
                keep_for=["debug"],
                reason="v0.9a composed semantic candidate is debug-only until detail rollout conditions are met",
            )
        )
    return suppressions


def _public_voice_detail_rollout_active_for_packet(
    *,
    packet: Mapping[str, Any],
    public_main_clusters: Sequence[NatalPromiseClusterV1],
) -> bool:
    if not (
        _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9")
        and _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT")
        and _env_enabled("ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT")
    ):
        return False
    if str(packet.get("source_type") or "").strip() != "composed_semantic":
        return False
    if str(packet.get("family") or "").strip() != "career_route":
        return False
    if str(packet.get("subtype") or "").strip() != "public_voice":
        return False
    public_eligibility = packet.get("public_eligibility") if isinstance(packet.get("public_eligibility"), Mapping) else {}
    if not bool(public_eligibility.get("detail_eligible")):
        return False
    domain_family = str(packet.get("_domain_family") or packet.get("domain") or "").strip()
    matching_owners = [cluster for cluster in public_main_clusters if cluster.domain_family == domain_family]
    if not matching_owners:
        return False
    return any(_cluster_fallback_quality(cluster) == "raw_generic_fallback" for cluster in matching_owners)


def _build_audit_metrics_and_warnings(
    *,
    candidate_packets: Sequence[Mapping[str, Any]],
    clusters: Sequence[NatalPromiseClusterV1],
    surface_plan: ClusterSurfacePlanV1,
    suppressed_packets: Sequence[PacketSuppressionStateV1],
) -> dict[str, Any]:
    warnings: list[str] = []
    missing_flags = _missing_candidate_flags(candidate_packets)
    warnings.extend(missing_flags)

    support_detail_empty = not surface_plan.public_support_cluster_ids and not surface_plan.detail_cluster_ids
    if support_detail_empty:
        warnings.append("support_detail_empty")

    generic_public_main_count = _generic_public_main_count(clusters, surface_plan)
    if generic_public_main_count > 0:
        warnings.append("generic_fallback_public_main")

    unique_candidate_count = len(
        {
            str(packet.get("theme_key") or packet.get("id") or "").strip()
            for packet in candidate_packets
            if str(packet.get("theme_key") or packet.get("id") or "").strip()
        }
    )
    if len(candidate_packets) < 10 or unique_candidate_count < 8:
        warnings.append("thin_candidate_inventory")

    chart_fact_mismatch = sum(1 for packet in candidate_packets if packet.get("chart_facts_match") is False)
    v0_6_count = sum(
        1
        for packet in candidate_packets
        if isinstance(packet.get("meta"), Mapping) and bool((packet.get("meta") or {}).get("v0_6_discovery"))
    )
    v8_duplication = _v8_duplication_proxy(clusters, surface_plan)
    if v0_6_count >= 3 and (
        generic_public_main_count > 0
        or support_detail_empty
        or len(missing_flags) >= 2
    ):
        warnings.append("mixed_chart_undercovered")

    health_score = 100
    health_score -= 12 * len(missing_flags)
    health_score -= 10 if support_detail_empty else 0
    health_score -= min(18, generic_public_main_count * 6)
    health_score -= 10 if "thin_candidate_inventory" in warnings else 0
    health_score -= 8 if "mixed_chart_undercovered" in warnings else 0
    health_score -= min(8, v8_duplication * 4)
    health_score -= min(6, chart_fact_mismatch * 2)
    health_score = max(0, min(100, health_score))
    candidate_source_type_distribution = _packet_source_type_distribution(candidate_packets)
    composed_family_distribution = _composed_candidate_family_distribution(candidate_packets)
    composed_confidence_distribution = _composed_candidate_confidence_distribution(candidate_packets)
    composed_public_eligibility_distribution = _composed_candidate_public_eligibility_distribution(candidate_packets)
    composed_subtype_distribution = _composed_candidate_subtype_distribution(candidate_packets)
    composed_cross_family_overlap_count = _composed_cross_family_overlap_count(candidate_packets)
    composed_v0_9b_confidence_distribution = _composed_v0_9b_confidence_distribution(candidate_packets)
    composed_default_fallback_count = _composed_default_fallback_count(candidate_packets)
    cross_family_moon_ownership_count = _composed_cross_family_moon_ownership_count(candidate_packets)
    relationship_candidates_blocked_by_moon_ownership = (
        _composed_relationship_blocked_by_moon_ownership_count(candidate_packets)
    )
    composed_v0_9b_opportunity_severity = _composed_v0_9b_opportunity_severity(candidate_packets)
    composed_opportunity_analysis = _composed_opportunity_analysis(
        candidate_packets=candidate_packets,
        clusters=clusters,
        surface_plan=surface_plan,
    )
    composed_vs_generic_fallback_opportunities = composed_opportunity_analysis["opportunities"]
    public_main_source_type_distribution = _cluster_source_type_distribution(
        clusters=clusters,
        cluster_ids=surface_plan.public_main_cluster_ids,
    )

    return {
        "coverage_warnings": warnings,
        "audit_metrics": {
            "candidate_count": len(candidate_packets),
            "unique_candidate_count": unique_candidate_count,
            "public_main_count": len(surface_plan.public_main_cluster_ids),
            "public_support_count": len(surface_plan.public_support_cluster_ids),
            "detail_count": len(surface_plan.detail_cluster_ids),
            "fallback_public_main_count": generic_public_main_count,
            "missing_domain_flags": missing_flags,
            "v8_duplication": v8_duplication,
            "chart_fact_mismatch": chart_fact_mismatch,
            "health_score": health_score,
            "debug_only_discovery_count": v0_6_count,
            "composed_candidate_count": sum(composed_family_distribution.values()),
            "composed_candidate_family_distribution": composed_family_distribution,
            "composed_candidate_confidence_distribution": composed_confidence_distribution,
            "composed_candidate_public_eligibility_distribution": composed_public_eligibility_distribution,
            "composed_candidate_subtype_distribution": composed_subtype_distribution,
            "composed_v0_9b_confidence_distribution": composed_v0_9b_confidence_distribution,
            "composed_cross_family_overlap_count": composed_cross_family_overlap_count,
            "composed_default_fallback_count": composed_default_fallback_count,
            "cross_family_moon_ownership_count": cross_family_moon_ownership_count,
            "relationship_candidates_blocked_by_moon_ownership": relationship_candidates_blocked_by_moon_ownership,
            "composed_v0_9b_opportunity_severity": composed_v0_9b_opportunity_severity,
            "composed_opportunity_severity_distribution": composed_opportunity_analysis["severity_distribution"],
            "composed_vs_generic_fallback_opportunities": composed_vs_generic_fallback_opportunities,
            "composed_debug_observations": composed_opportunity_analysis["debug_observations"],
            "suppressed_packet_count": len(suppressed_packets),
            "candidate_source_type_distribution": candidate_source_type_distribution,
            "public_main_source_type_distribution": public_main_source_type_distribution,
        },
    }


def _missing_candidate_flags(candidate_packets: Sequence[Mapping[str, Any]]) -> list[str]:
    checks = [
        ("missing_identity_candidate", "identity"),
        ("missing_relationship_candidate", "relationship"),
        ("missing_career_candidate", "career"),
        ("missing_emotional_candidate", "emotional"),
        ("missing_mind_candidate", "mind"),
    ]
    warnings: list[str] = []
    for warning, discovery_domain in checks:
        if not any(_packet_supports_discovery_domain(packet, discovery_domain) for packet in candidate_packets):
            warnings.append(warning)
    return warnings


def _packet_supports_discovery_domain(packet: Mapping[str, Any], discovery_domain: str) -> bool:
    meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
    packet_id = str(packet.get("id") or "").strip().lower()
    packet_domain = str(packet.get("domain") or "").strip().lower()
    technical = " ".join(str(item).strip().lower() for item in (packet.get("technical_anchors") or []) if str(item).strip())
    if str(meta.get("discovery_domain") or "").strip().lower() == discovery_domain:
        return True
    if discovery_domain == "identity":
        return packet_domain == "identity" and not packet_id.startswith("identity_identity")
    if discovery_domain == "relationship":
        return packet_domain in {"relationship", "love", "emotional_depth"} and packet_id != "relationship_relationships"
    if discovery_domain == "career":
        return packet_domain in {"career", "visibility"} and packet_id != "career_career_visibility"
    if discovery_domain == "mind":
        return packet_domain in {"mind", "communication"} and packet_id != "mind_mind_system"
    if discovery_domain == "emotional":
        return (
            packet_domain in {"home_family", "inner_world", "emotional_world", "creativity"}
            or "ay" in technical
            or "moon" in technical
            or "ic" in technical
        )
    return False


def _generic_public_main_count(
    clusters: Sequence[NatalPromiseClusterV1],
    surface_plan: ClusterSurfacePlanV1,
) -> int:
    cluster_lookup = {cluster.id: cluster for cluster in clusters}
    return sum(
        1
        for cluster_id in surface_plan.public_main_cluster_ids
        if cluster_lookup.get(cluster_id) is not None and _is_generic_cluster(cluster_lookup[cluster_id])
    )


def _v8_duplication_proxy(
    clusters: Sequence[NatalPromiseClusterV1],
    surface_plan: ClusterSurfacePlanV1,
) -> int:
    cluster_lookup = {cluster.id: cluster for cluster in clusters}
    semantic_keys: list[str] = []
    for cluster_id in [
        *surface_plan.public_main_cluster_ids,
        *surface_plan.public_support_cluster_ids,
        *surface_plan.detail_cluster_ids,
    ]:
        cluster = cluster_lookup.get(cluster_id)
        if cluster is None:
            continue
        semantic_key = _cluster_semantic_key(cluster) or cluster.cluster_label
        if semantic_key:
            semantic_keys.append(f"{cluster.domain_family}:{semantic_key}")
    duplicates = 0
    seen: set[str] = set()
    for key in semantic_keys:
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
    return duplicates


def _composed_candidate_packets(candidate_packets: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return [
        packet
        for packet in candidate_packets
        if str(packet.get("source_type") or "").strip() == "composed_semantic"
    ]


def _composed_candidate_family_distribution(candidate_packets: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for packet in _composed_candidate_packets(candidate_packets):
        family = str(packet.get("family") or ((packet.get("meta") or {}) if isinstance(packet.get("meta"), Mapping) else {}).get("v0_9_family") or "unknown").strip()
        counts[family] = counts.get(family, 0) + 1
    return counts


def _composed_candidate_confidence_distribution(candidate_packets: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0}
    for packet in _composed_candidate_packets(candidate_packets):
        tier = str(
            packet.get("confidence_tier")
            or ((packet.get("meta") or {}) if isinstance(packet.get("meta"), Mapping) else {}).get("confidence_tier")
            or "low"
        ).strip().lower()
        if tier in counts:
            counts[tier] += 1
    return counts


def _composed_candidate_subtype_distribution(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Per-family subtype counts across composed_semantic candidates.

    Used by the v0.9b debug-only rollout to audit how often each subtype
    fires and whether the default-fallback subtype dominates the
    distribution.
    """
    by_family: dict[str, dict[str, int]] = {}
    for packet in _composed_candidate_packets(candidate_packets):
        family = str(packet.get("family") or "").strip()
        if not family:
            meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
            family = str(meta.get("v0_9_family") or "unknown").strip() or "unknown"
        subtype = str(packet.get("subtype") or "").strip() or "unknown"
        bucket = by_family.setdefault(family, {})
        bucket[subtype] = bucket.get(subtype, 0) + 1
    return by_family


def _composed_v0_9b_confidence_distribution(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Confidence-bucket histogram per v0.9b family.

    Buckets match the v0.9b plan §3 distribution targets so audit reports
    can read the live histogram directly.
    """
    buckets = ("ge_0_80", "0_70_0_80", "0_60_0_70", "lt_0_60")
    by_family: dict[str, dict[str, int]] = {}
    for packet in _composed_candidate_packets(candidate_packets):
        family = str(packet.get("family") or "").strip()
        if family not in {"relationship_route", "moon_signature"}:
            continue
        confidence = _safe_float(packet.get("confidence"), 0.0)
        if confidence >= 0.80:
            key = "ge_0_80"
        elif confidence >= 0.70:
            key = "0_70_0_80"
        elif confidence >= 0.60:
            key = "0_60_0_70"
        else:
            key = "lt_0_60"
        bucket = by_family.setdefault(family, {b: 0 for b in buckets})
        bucket[key] += 1
    return by_family


def _composed_default_fallback_count(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Per-family / per-subtype count of default-fallback composed candidates.

    A candidate is "default-fallback" when its meta marks
    ``subtype_default_fallback=True`` — i.e. the subtype scoring path
    failed to pick a clearly winning channel and the family's neutral
    default (``trust_steadiness`` for relationship_route,
    ``emotional_rhythm`` for moon_signature) fired with a penalty.
    """
    by_family: dict[str, dict[str, int]] = {}
    for packet in _composed_candidate_packets(candidate_packets):
        meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
        if not bool(meta.get("subtype_default_fallback")):
            continue
        family = str(packet.get("family") or "").strip() or "unknown"
        subtype = str(packet.get("subtype") or "").strip() or "unknown"
        bucket = by_family.setdefault(family, {})
        bucket[subtype] = bucket.get(subtype, 0) + 1
    return by_family


def _composed_cross_family_moon_ownership_count(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> int:
    """Count of relationship_route candidates whose Moon evidence is owned
    by the moon_signature family (v0.9b.0.1 cross-family ownership rule).
    """
    count = 0
    for packet in _composed_candidate_packets(candidate_packets):
        if str(packet.get("family") or "") != "relationship_route":
            continue
        meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
        if str(meta.get("moon_evidence_owned_by") or "") == "moon_signature":
            count += 1
    return count


def _composed_relationship_blocked_by_moon_ownership_count(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> int:
    """Count of relationship candidates flagged with
    ``future_renderer_eligibility_blocked=True`` via the Moon ownership rule.
    """
    count = 0
    for packet in _composed_candidate_packets(candidate_packets):
        if str(packet.get("family") or "") != "relationship_route":
            continue
        elig = packet.get("public_eligibility") if isinstance(packet.get("public_eligibility"), Mapping) else {}
        if bool(elig.get("future_renderer_eligibility_blocked")):
            count += 1
    return count


def _composed_v0_9b_opportunity_severity(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> dict[str, dict[str, int]]:
    """Classify v0.9b composed candidates into the three opportunity buckets.

    Classification rules (v0.9b.0.1, calibration-aware):

    * ``debug_observation_only`` — default-fallback candidate, OR
      confidence < 0.70, OR relationship candidate where the Moon family
      took ownership of the evidence.
    * ``high_priority_opportunity`` — non-fallback, confidence >= 0.80,
      not Moon-owned-elsewhere.
    * ``medium_priority_opportunity`` — non-fallback,
      0.70 <= confidence < 0.80, not Moon-owned-elsewhere.
    """
    severity = {
        "relationship_route": {
            "high_priority_opportunity": 0,
            "medium_priority_opportunity": 0,
            "debug_observation_only": 0,
        },
        "moon_signature": {
            "high_priority_opportunity": 0,
            "medium_priority_opportunity": 0,
            "debug_observation_only": 0,
        },
    }
    for packet in _composed_candidate_packets(candidate_packets):
        family = str(packet.get("family") or "").strip()
        if family not in severity:
            continue
        meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
        elig = packet.get("public_eligibility") if isinstance(packet.get("public_eligibility"), Mapping) else {}
        confidence = _safe_float(packet.get("confidence"), 0.0)
        is_fallback = bool(meta.get("subtype_default_fallback"))
        moon_owned_elsewhere = (
            family == "relationship_route"
            and (
                bool(elig.get("future_renderer_eligibility_blocked"))
                or str(meta.get("moon_evidence_owned_by") or "") == "moon_signature"
            )
        )
        if is_fallback or moon_owned_elsewhere or confidence < 0.70:
            severity[family]["debug_observation_only"] += 1
        elif confidence >= 0.80:
            severity[family]["high_priority_opportunity"] += 1
        else:
            severity[family]["medium_priority_opportunity"] += 1
    return severity


def _composed_cross_family_overlap_count(
    candidate_packets: Sequence[Mapping[str, Any]],
) -> int:
    """Count of composed candidates whose ``evidence_trace.cross_family_overlap``
    is non-empty — i.e. Moon evidence (or any cross-family signal) is
    shared between relationship_route and moon_signature."""
    count = 0
    for packet in _composed_candidate_packets(candidate_packets):
        trace = packet.get("evidence_trace") if isinstance(packet.get("evidence_trace"), Mapping) else {}
        overlap = trace.get("cross_family_overlap") if isinstance(trace.get("cross_family_overlap"), Sequence) else []
        if overlap:
            count += 1
    return count


def _composed_candidate_public_eligibility_distribution(candidate_packets: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = {
        "debug_eligible": 0,
        "detail_eligible": 0,
        "public_support_eligible": 0,
        "public_main_eligible": 0,
        "debug_only": 0,
    }
    for packet in _composed_candidate_packets(candidate_packets):
        eligibility = packet.get("public_eligibility") if isinstance(packet.get("public_eligibility"), Mapping) else {}
        if not eligibility:
            meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
            eligibility = meta.get("public_eligibility") if isinstance(meta.get("public_eligibility"), Mapping) else {}
        debug_eligible = bool(eligibility.get("debug_eligible"))
        detail_eligible = bool(eligibility.get("detail_eligible"))
        public_support_eligible = bool(eligibility.get("public_support_eligible"))
        public_main_eligible = bool(eligibility.get("public_main_eligible"))
        counts["debug_eligible"] += 1 if debug_eligible else 0
        counts["detail_eligible"] += 1 if detail_eligible else 0
        counts["public_support_eligible"] += 1 if public_support_eligible else 0
        counts["public_main_eligible"] += 1 if public_main_eligible else 0
        if debug_eligible and not detail_eligible and not public_support_eligible and not public_main_eligible:
            counts["debug_only"] += 1
    return counts


_GENERIC_MAIN_PACKET_IDS = {
    "identity_identity",
    "relationship_relationships",
    "career_career_visibility",
    "mind_mind_system",
}


def _composed_opportunity_analysis(
    *,
    candidate_packets: Sequence[Mapping[str, Any]],
    clusters: Sequence[NatalPromiseClusterV1],
    surface_plan: ClusterSurfacePlanV1,
) -> dict[str, Any]:
    cluster_lookup = {cluster.id: cluster for cluster in clusters}
    public_main_clusters = [
        cluster_lookup[cluster_id]
        for cluster_id in surface_plan.public_main_cluster_ids
        if cluster_lookup.get(cluster_id) is not None
    ]
    if not public_main_clusters:
        return {
            "opportunities": [],
            "debug_observations": [],
            "severity_distribution": {
                "high_priority_opportunity": 0,
                "medium_priority_opportunity": 0,
                "debug_observation_only": 0,
            },
        }

    domain_to_clusters: dict[str, list[NatalPromiseClusterV1]] = {}
    for cluster in public_main_clusters:
        domain_to_clusters.setdefault(cluster.domain_family, []).append(cluster)

    opportunities: list[dict[str, Any]] = []
    debug_observations: list[dict[str, Any]] = []
    severity_distribution = {
        "high_priority_opportunity": 0,
        "medium_priority_opportunity": 0,
        "debug_observation_only": 0,
    }
    for packet in _composed_candidate_packets(candidate_packets):
        domain_family = str(packet.get("_domain_family") or packet.get("domain") or "").strip()
        matching_clusters = domain_to_clusters.get(domain_family, [])
        if not matching_clusters:
            continue
        owner_qualities = [_cluster_fallback_quality(cluster) for cluster in matching_clusters]
        raw_generic_clusters = [cluster for cluster in matching_clusters if _cluster_fallback_quality(cluster) == "raw_generic_fallback"]
        customized_clusters = [cluster for cluster in matching_clusters if _cluster_fallback_quality(cluster) == "customized_fallback_with_bespoke_copy"]
        cluster_specific_clusters = [cluster for cluster in matching_clusters if _cluster_fallback_quality(cluster) == "cluster_specific_fallback"]
        exact_clusters = [cluster for cluster in matching_clusters if _cluster_fallback_quality(cluster) == "exact_registry"]
        confidence_tier = str(packet.get("confidence_tier") or "").strip().lower()
        has_scene_specificity = _packet_has_scene_specificity(packet)
        packet_family = str(packet.get("family") or "").strip()

        if (
            raw_generic_clusters
            and confidence_tier in {"medium", "high"}
            and has_scene_specificity
        ):
            severity = "high_priority_opportunity"
            target_clusters = raw_generic_clusters
        elif (
            packet_family == "career_route"
            and customized_clusters
            and confidence_tier in {"medium", "high"}
            and has_scene_specificity
        ):
            severity = "medium_priority_opportunity"
            target_clusters = customized_clusters
        else:
            severity = "debug_observation_only"
            target_clusters = matching_clusters
            if packet_family == "identity_route" and (cluster_specific_clusters or exact_clusters or customized_clusters):
                target_clusters = cluster_specific_clusters or exact_clusters or customized_clusters or matching_clusters

        entry = {
            "packet_id": str(packet.get("id") or "").strip(),
            "family": packet_family,
            "domain": str(packet.get("domain") or "").strip(),
            "confidence_tier": str(packet.get("confidence_tier") or "").strip(),
            "severity": severity,
            "current_owner_quality": sorted(set(owner_qualities)),
            "target_generic_cluster_ids": [cluster.id for cluster in target_clusters],
            "target_main_packet_ids": [cluster.main_packet_id for cluster in target_clusters],
        }
        severity_distribution[severity] += 1
        if severity == "debug_observation_only":
            debug_observations.append(entry)
            continue
        opportunities.append(entry)

    return {
        "opportunities": opportunities,
        "debug_observations": debug_observations,
        "severity_distribution": severity_distribution,
    }


def _cluster_fallback_quality(cluster: NatalPromiseClusterV1) -> str:
    source_type = str(cluster.source_type or "").strip()
    main_packet_id = str(cluster.main_packet_id or "").strip()
    if source_type == "exact_registry":
        return "exact_registry"
    if source_type != "generic_fallback":
        return source_type
    if main_packet_id in _GENERIC_MAIN_PACKET_IDS:
        return "raw_generic_fallback"
    if _cluster_owner_semantically_acceptable(cluster):
        return "cluster_specific_fallback"
    if str(cluster.distinct_lived_scene or "").strip():
        return "customized_fallback_with_bespoke_copy"
    return "raw_generic_fallback"


def _cluster_owner_semantically_acceptable(cluster: NatalPromiseClusterV1) -> bool:
    main_packet_id = str(cluster.main_packet_id or "").strip()
    scene = str(cluster.distinct_lived_scene or "").strip()
    semantic_key = _cluster_semantic_key(cluster)
    if main_packet_id in _GENERIC_MAIN_PACKET_IDS:
        return False
    if "chart_exact" in main_packet_id and len(scene.split()) >= 5:
        return True
    if semantic_key and len(scene.split()) >= 5:
        return True
    return False


def _packet_has_scene_specificity(packet: Mapping[str, Any]) -> bool:
    lived_scene = str(packet.get("lived_scene") or "").strip()
    return len(lived_scene.split()) >= 5


def _normalize_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    packet_id = str(packet.get("id") or "").strip()
    domain_family = _domain_family(packet)
    promise_type = str(packet.get("promise_type") or "").strip()
    promise_type_family = _promise_type_family(promise_type)
    lived_scene = str(packet.get("lived_scene") or "").strip()
    subtype = _packet_subtype(packet=packet, domain_family=domain_family)
    theme_tokens = _theme_tokens(packet)
    anchor_ids = _anchor_ids(packet)
    meta = packet.get("meta") if isinstance(packet.get("meta"), Mapping) else {}
    return {
        **dict(packet),
        "_domain_family": domain_family,
        "_promise_type_family": promise_type_family,
        "_lived_scene_fingerprint": _fingerprint_text(lived_scene, limit=12),
        "_lived_scene_family": _fingerprint_text(lived_scene, limit=6),
        "_anchor_group_fingerprint": _anchor_group_fingerprint(anchor_ids),
        "_anchor_ids": anchor_ids,
        "_theme_tokens": theme_tokens,
        "_subtype": subtype,
        "_packet_id": packet_id,
        "_human_angle_fingerprint": _human_angle_fingerprint(packet, subtype=subtype),
        "_is_auxiliary": bool(meta.get("auxiliary")) or packet_id.endswith("_aux"),
        "_is_overlay": packet_id.endswith("_overlay"),
    }


def _domain_family(packet: Mapping[str, Any]) -> str:
    domain = str(packet.get("domain") or "").strip().lower()
    packet_id = str(packet.get("id") or "").strip().lower()
    text = " ".join(
        [
            packet_id,
            " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip()),
            " ".join(str(item).strip() for item in (packet.get("source_evidence_ids") or []) if str(item).strip()),
        ]
    ).lower()
    if domain in {"mind", "communication"}:
        return "mind"
    if domain in {"action", "daily_life"}:
        return "action"
    if domain in {"axis_tension"}:
        return "axis_tension"
    if domain in {"community", "vision"}:
        return "community"
    if domain in {"inner_world", "spirituality", "emotional_world"}:
        return "inner_world"
    if domain in {"home_family", "roots"}:
        return "home_family"
    if domain in {"relationship", "relationships", "love", "emotional_depth"}:
        return "relationship"
    if domain in {"creativity"}:
        return "creativity"
    if domain in {"career", "visibility"}:
        return "career"
    if domain in {"identity", "behavior_reflex"}:
        return "identity"
    if any(token in text for token in ("pressure", "resilience", "mars", "pluto", "saturn_trine_pluto", "saturn_pluto")):
        return "action_pressure"
    if any(token in text for token in ("community", "social", "aquarius", "kova")):
        return "community"
    if any(token in text for token in ("money", "worth", "self_worth", "2. ev", "2th house")):
        return "money"
    return "identity"


def _promise_type_family(promise_type: str) -> str:
    mapping = {
        "gift": "gift_like",
        "love_style": "love_like",
        "need": "need_like",
        "mind_style": "mind_like",
        "mind_identity": "mind_like",
        "career_signature": "career_like",
        "career_friction_to_power": "career_like",
        "wound_to_gift": "wound_like",
        "shadow_or_friction": "shadow_like",
        "behavior_reflex": "identity_like",
        "identity_style": "identity_like",
        "drive": "identity_like",
        "social_mind_style": "mind_like",
        "relationship_need": "need_like",
        "roots_transformation": "wound_like",
        "home_family_signature": "need_like",
        "creative_emotional_style": "gift_like",
        "creative_signature": "gift_like",
        "identity_action_style": "action_like",
        "action_friction_to_strength": "action_like",
        "inner_pressure_to_maturity": "wound_like",
        "emotional_home_signature": "need_like",
        "career_mind_signature": "career_like",
        "axis_tension": "axis_like",
        "collective_identity": "community_like",
        "community_signature": "community_like",
        "relationship_wound_to_gift": "wound_like",
        "career_love_style": "love_like",
        "life_direction_axis": "axis_like",
    }
    return mapping.get(str(promise_type or "").strip(), "generic")


def _packet_subtype(*, packet: Mapping[str, Any], domain_family: str) -> str:
    packet_id = str(packet.get("id") or "").strip().lower()
    anchors = " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip()).lower()
    if domain_family == "relationship":
        if "harmony_wound_depth" in packet_id or "libra_dsc_chiron_scorpio_7h" in packet_id:
            return "harmony_wound_depth"
        if "public_love_style_responsibility" in packet_id or "venus_capricorn_10h" in packet_id:
            return "public_love_responsibility"
        if "affection_gift" in packet_id or "moon_trine_venus" in packet_id:
            return "affection_gift"
        if "trust_bond" in packet_id or "venus_trine_saturn" in packet_id:
            return "trust_bond"
        if "trust_threshold_silent_desire" in packet_id or "dsc_scorpio_ruler_mars_pisces_12h" in packet_id:
            return "trust_threshold_silent_desire"
        if "freedom_responsibility_sensitivity" in packet_id or "aquarius_dsc_saturn_pisces_7h" in packet_id:
            return "freedom_responsibility_sensitivity"
        if "hidden_romantic_pride" in packet_id or "venus_leo_12h" in packet_id:
            return "hidden_romantic_pride"
        if "attraction_signal" in packet_id or "venus_trine_mars" in packet_id:
            return "attraction_signal"
        if "emotional_routine_sensitivity" in packet_id or "moon_scorpio_6h" in packet_id:
            return "emotional_routine_sensitivity"
        if "private_love_inner_beauty" in packet_id or "venus_taurus_12h" in packet_id:
            return "private_love_inner_beauty"
        if "relationship_power_depth" in packet_id or "pluto_7h" in packet_id:
            return "relationship_power_depth"
        if "attachment_architecture" in packet_id or "moon_leo_8h" in packet_id or ("7. ev" in anchors and "ay 8. ev" in anchors):
            return "attachment_architecture"
        if "hidden_private_love" in packet_id or "venus_sagittarius_12h" in packet_id:
            return "hidden_private_love_pattern"
    if domain_family == "career":
        if "public_voice_strategic_mind" in packet_id or "mercury_capricorn_mc" in packet_id:
            return "public_voice_strategic_mind"
        if "public_style_responsibility" in packet_id or "capricorn_10h_mercury_venus_neptune" in packet_id:
            return "public_style_responsibility"
        if "internal_visibility_maturation" in packet_id or "career_duplicate" in packet_id or "venus_sagittarius_12h" in packet_id:
            return "internal_visibility_maturation"
        if "invisible_preparation" in packet_id or "mc_capricorn_ruler_saturn_pisces_12h" in packet_id:
            return "invisible_preparation"
        if "steady_public_drive" in packet_id or "mc_taurus_mars_10h" in packet_id:
            return "steady_public_drive"
        if "public_power_roots_tension" in packet_id or "mars_opposite_pluto" in packet_id:
            return "public_power_roots_tension"
        if "healing_voice" in packet_id or ("chiron" in packet_id and "mc" in packet_id):
            return "healing_voice"
    if domain_family == "mind":
        if "structured_originality" in packet_id or "saturn_sextile_uranus" in packet_id:
            return "structured_originality"
        if "speech_decision_language" in packet_id or "saturn_3h" in packet_id:
            return "speech_decision_language"
        if "social_emotional_intelligence" in packet_id or "sun_mercury_cancer_11h" in packet_id:
            return "social_emotional_intelligence"
        if "deep_speech_psychological_learning" in packet_id or "jupiter_scorpio_3h" in packet_id:
            return "deep_speech_psychological_learning"
        if "social_intuition_mind" in packet_id or "mercury_pisces_11h" in packet_id:
            return "social_intuition_mind"
        if "deep_mind_pressure" in packet_id or "mercury_square_pluto" in packet_id:
            return "deep_mind_pressure"
    if domain_family == "identity":
        if "action_through_balance" in packet_id or "aries_asc_mars_libra_6h" in packet_id:
            return "action_through_balance"
        if "collective_identity" in packet_id or "sun_aquarius_11h" in packet_id:
            return "collective_identity"
        if "self_construction" in packet_id or "capricorn_asc" in packet_id:
            return "self_construction"
        if "hidden_value_identity" in packet_id or "taurus_asc_venus_12h" in packet_id:
            return "hidden_value_identity"
        if "soft_hidden_magnetism" in packet_id or "venus_12h_conjunct_asc" in packet_id:
            return "soft_hidden_magnetism"
        if "unsettled_outer_signal" in packet_id or "uranus_square_asc_venus" in packet_id:
            return "unsettled_outer_signal"
        if "warm_visibility_belonging" in packet_id or "leo_asc_sun_cancer_11h" in packet_id:
            return "warm_visibility_belonging"
        if "visible_sensitivity_self_correction" in packet_id or "chiron_virgo_1h" in packet_id:
            return "visible_sensitivity_self_correction"
    if domain_family == "inner_world":
        if "private_pressure_hidden_self_control" in packet_id or "saturn_aries_12h" in packet_id:
            return "private_pressure"
        if "inner_world_saturation" in packet_id or "pisces_12h_stellium" in packet_id:
            return "inner_world_saturation"
        if "private_maturity_boundary_sensitivity" in packet_id or "saturn_pisces_12h" in packet_id:
            return "private_maturity"
        if "hidden_action_soft_drive" in packet_id or "mars_pisces_12h" in packet_id:
            return "hidden_action_soft_drive"
        if "private_will_and_hidden_drive" in packet_id or "sun_mars_pisces_12h" in packet_id:
            return "private_will_hidden_drive"
    if domain_family == "home_family":
        if "home_security_roots" in packet_id or "moon_cancer_ic" in packet_id:
            return "home_security_roots"
        if "roots_inner_security_transformation" in packet_id or "pluto_node_scorpio_4h" in packet_id:
            return "roots_inner_security_transformation"
        if "private_emotional_inheritance" in packet_id or "ic_scorpio_pluto_node" in packet_id:
            return "private_emotional_inheritance"
    if domain_family == "creativity":
        if "structured_imagination" in packet_id or "moon_uranus_neptune_capricorn_5h" in packet_id:
            return "structured_imagination"
        if "serious_heart_creative_form" in packet_id or "moon_capricorn_5h" in packet_id:
            return "serious_heart_creative_form"
    if domain_family == "action_pressure":
        return "resilience_under_pressure"
    if domain_family == "action":
        if "action_restraint" in packet_id or "mars_opposite_saturn" in packet_id:
            return "action_restraint"
        if "action_through_balance" in packet_id or "aries_asc_mars_libra_6h" in packet_id:
            return "action_through_balance"
    if domain_family == "axis_tension":
        if "private_security_public_voice_axis" in packet_id or "moon_mercury_ic_mc" in packet_id:
            return "private_security_public_voice_axis"
        if "service_action_axis" in packet_id or "libra_aries_6h_12h" in packet_id:
            return "service_action_axis"
    if domain_family == "community":
        if "collective_identity" in packet_id or "sun_aquarius_11h" in packet_id:
            return "collective_identity"
        if "future_collective_signal" in packet_id or "aquarius_11h" in packet_id:
            return "future_collective_signal"
    return ""


def _theme_tokens(packet: Mapping[str, Any]) -> set[str]:
    raw = " ".join(
        [
            str(packet.get("id") or ""),
            str(packet.get("direct_meaning") or ""),
            str(packet.get("gift") or ""),
            str(packet.get("shadow_or_friction") or ""),
            str(packet.get("growth_direction") or ""),
            str(packet.get("_subtype") or ""),
        ]
    )
    tokens = _tokenize(raw)
    return {token for token in tokens if len(token) > 3}


def _human_angle_fingerprint(packet: Mapping[str, Any], *, subtype: str) -> str:
    if subtype:
        return subtype
    raw = " ".join(
        [
            str(packet.get("direct_meaning") or ""),
            str(packet.get("gift") or ""),
            str(packet.get("shadow_or_friction") or ""),
            str(packet.get("lived_scene") or ""),
        ]
    )
    return _fingerprint_text(raw, limit=10)


def _anchor_ids(packet: Mapping[str, Any]) -> list[str]:
    out: list[str] = []
    for value in [
        *(packet.get("technical_anchors") or []),
        *(packet.get("source_evidence_ids") or []),
    ]:
        clean = str(value).strip()
        if not clean:
            continue
        canonical = _normalize_text(clean)
        if canonical and canonical not in out:
            out.append(canonical)
    return out


def _anchor_group_fingerprint(anchor_ids: Sequence[str]) -> str:
    if not anchor_ids:
        return ""
    return "|".join(sorted(anchor_ids[:3]))


def _build_focus_map(packets: Sequence[Mapping[str, Any]]) -> list[DomainFocusScoreV1]:
    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for packet in packets:
        grouped[str(packet.get("_domain_family") or "identity")].append(packet)
    scores: list[DomainFocusScoreV1] = []
    for domain_family, items in grouped.items():
        strength_sum = min(1.0, sum(_safe_float(item.get("strength"), 0.0) for item in items) / 2.35)
        max_strength = max((_safe_float(item.get("strength"), 0.0) for item in items), default=0.0)
        chart_ruler = _avg_feature(items, _has_chart_ruler_signal)
        angularity = _avg_feature(items, _has_angular_signal)
        luminary = _avg_feature(items, _has_luminary_signal)
        house_chain = _avg_feature(items, _has_house_chain_signal)
        repeated = min(1.0, len({_base_packet_id(item) for item in items}) / 2.5)
        contradiction = min(
            1.0,
            sum(_safe_float((item.get("scoring_breakdown") or {}).get("contradiction"), 0.0) for item in items) / max(1, len(items)),
        )
        archetype = min(
            1.0,
            sum(_safe_float((item.get("scoring_breakdown") or {}).get("archetype"), 0.0) for item in items) / max(1, len(items)),
        )
        score = (
            strength_sum * 0.27
            + max_strength * 0.12
            + chart_ruler * 0.16
            + angularity * 0.14
            + luminary * 0.10
            + house_chain * 0.10
            + repeated * 0.06
            + contradiction * 0.03
            + archetype * 0.02
        )
        if chart_ruler >= 0.75 and angularity >= 0.75:
            score += 0.08
        if chart_ruler >= 0.75 and angularity >= 0.75 and house_chain >= 0.5:
            score += 0.05
        if max_strength >= 0.8 and (chart_ruler >= 0.5 or angularity >= 0.5):
            score += 0.06
        if repeated >= 0.66 and (luminary >= 0.5 or house_chain >= 0.5):
            score += 0.04
        normalized = round(min(1.0, _apply_chart_defining_focus_floor(domain_family, items, score)), 4)
        scores.append(
            DomainFocusScoreV1(
                domain=domain_family,
                score=normalized,
                tier=_focus_tier(normalized),
                packet_ids=[str(item.get("id") or "").strip() for item in items if str(item.get("id") or "").strip()],
                evidence_summary=_focus_evidence_summary(items),
                scoring_breakdown={
                    "packet_strength_sum": round(strength_sum, 4),
                    "chart_ruler": round(chart_ruler, 4),
                    "angularity": round(angularity, 4),
                    "luminary": round(luminary, 4),
                    "house_chain": round(house_chain, 4),
                    "repeated_support": round(repeated, 4),
                    "contradiction": round(contradiction, 4),
                    "archetype_confidence": round(archetype, 4),
                },
            )
        )
    scores.sort(key=lambda item: (-item.score, item.domain))
    return scores


def _apply_chart_defining_focus_floor(
    domain_family: str,
    items: Sequence[Mapping[str, Any]],
    score: float,
) -> float:
    """Keep additive chart-exact overlays from losing to generic multi-packet fallbacks.

    v0.8 introduces several one-packet axis signatures. The generic focus
    formula rewards repeated packet support, which is correct for fallback
    inventory but under-reads single, chart-defining angular/luminary packets
    such as Moon Cancer near IC.
    """

    subtypes = {_packet_subtype(packet=item, domain_family=domain_family) for item in items}
    ids = {str(item.get("id") or "").strip() for item in items}
    if domain_family == "home_family" and "home_security_roots" in subtypes:
        return max(score, 0.88)
    if domain_family == "action" and {"action_through_balance", "action_restraint"}.intersection(subtypes):
        return max(score, 0.68)
    if domain_family == "axis_tension" and "private_security_public_voice_axis" in subtypes:
        return max(score, 0.88)
    if domain_family == "community" and "collective_identity" in subtypes:
        return max(score, 0.72)
    if domain_family == "relationship" and "harmony_wound_depth" in subtypes:
        return max(score, 0.68)
    if domain_family == "inner_world" and any("saturn_aries_12h_private_pressure" in packet_id for packet_id in ids):
        return max(score, 0.46)
    return score


def _avg_feature(items: Sequence[Mapping[str, Any]], fn: Any) -> float:
    if not items:
        return 0.0
    return sum(1.0 if fn(item) else 0.0 for item in items) / float(len(items))


def _has_chart_ruler_signal(packet: Mapping[str, Any]) -> bool:
    text = " ".join(str(item).strip() for item in (packet.get("source_evidence_ids") or []) if str(item).strip())
    anchors = " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip())
    packet_id = str(packet.get("id") or "").strip().lower()
    lowered_anchors = anchors.lower()
    return (
        "->ruler" in text
        or "yükselen" in lowered_anchors
        or "asc" in lowered_anchors
        or "mc" in lowered_anchors
        or "midheaven" in lowered_anchors
        or "capricorn_asc" in packet_id
    )


def _has_angular_signal(packet: Mapping[str, Any]) -> bool:
    text = " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip()).lower()
    return any(token in text for token in ("1. ev", "4. ev", "7. ev", "10. ev", "yükselen", "mc"))


def _has_luminary_signal(packet: Mapping[str, Any]) -> bool:
    text = " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip()).lower()
    return "ay" in text or "güneş" in text or "moon" in text or "sun" in text


def _has_house_chain_signal(packet: Mapping[str, Any]) -> bool:
    text = " ".join(str(item).strip() for item in (packet.get("source_evidence_ids") or []) if str(item).strip()).lower()
    anchors = " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip()).lower()
    return "->ruler" in text or "route" in anchors


def _focus_tier(score: float) -> FocusTier:
    if score >= 0.85:
        return "strong"
    if score >= 0.65:
        return "medium_strong"
    if score >= 0.45:
        return "supporting"
    return "detail_only"


def _focus_evidence_summary(items: Sequence[Mapping[str, Any]]) -> list[str]:
    out: list[str] = []
    if any(_has_chart_ruler_signal(item) for item in items):
        out.append("chart ruler support")
    if any(_has_angular_signal(item) for item in items):
        out.append("angular support")
    if any(_has_luminary_signal(item) for item in items):
        out.append("luminary support")
    if any(_has_house_chain_signal(item) for item in items):
        out.append("house-chain support")
    if len(items) >= 2:
        out.append("repeated packet support")
    return out[:4]


def _build_primary_clusters(
    packets: Sequence[Mapping[str, Any]],
    focus_map: Sequence[DomainFocusScoreV1],
) -> list[NatalPromiseClusterV1]:
    clusters: list[dict[str, Any]] = []
    for packet in sorted(packets, key=lambda item: (-_safe_float(item.get("strength"), 0.0), str(item.get("id") or ""))):
        domain_family = str(packet.get("_domain_family") or "identity")
        candidates = [cluster for cluster in clusters if cluster["domain_family"] == domain_family]
        best_cluster = None
        best_score = 0.0
        for cluster in candidates:
            fit = _cluster_fit(packet, cluster)
            if fit > best_score:
                best_cluster = cluster
                best_score = fit
        if best_cluster is not None and (best_score >= 0.58 or (best_score >= 0.45 and _focus_score(domain_family, focus_map) >= 0.7)):
            best_cluster["members"].append(packet)
        else:
            clusters.append(
                {
                    "domain_family": domain_family,
                    "cluster_label": _cluster_label(packet),
                    "members": [packet],
                }
            )
    out: list[NatalPromiseClusterV1] = []
    for cluster in clusters:
        members = list(cluster["members"])
        main_packet = _pick_cluster_main_packet(members, cluster["domain_family"], focus_map)
        cluster_id = _cluster_id(cluster["domain_family"], cluster["cluster_label"], main_packet)
        cluster_model = NatalPromiseClusterV1(
            id=cluster_id,
            domain=str(main_packet.get("domain") or cluster["domain_family"]),
            domain_family=cluster["domain_family"],
            cluster_label=cluster["cluster_label"],
            source_type="legacy_graph",
            cluster_strength=0.0,
            public_card_priority=0.0,
            focus_tier=_focus_tier(_focus_score(cluster["domain_family"], focus_map)),
            target_surface_role="detail",
            main_packet_id=str(main_packet.get("id") or ""),
            packet_members=[],
            shared_themes=_shared_themes(members),
            distinct_lived_scene=str(main_packet.get("lived_scene") or ""),
            promise_types=_unique_strings(str(item.get("promise_type") or "") for item in members),
            technical_anchor_ids=_unique_strings(anchor for item in members for anchor in (item.get("_anchor_ids") or [])),
            dedupe_fingerprint=f"{cluster['domain_family']}|{cluster['cluster_label']}|{str(main_packet.get('_lived_scene_fingerprint') or '')}",
            selection_notes=[],
            scoring_breakdown={},
            subtypes=_unique_strings(str(item.get("_subtype") or "") for item in members),
        )
        _assign_member_roles(cluster_model, members)
        out.append(cluster_model)
    return out


def _cluster_fit(packet: Mapping[str, Any], cluster: Mapping[str, Any]) -> float:
    members = cluster.get("members") if isinstance(cluster.get("members"), Sequence) else []
    if not members:
        return 0.0
    sample = members[0]
    checks = {
        "same_domain_family": str(packet.get("_domain_family") or "") == str(cluster.get("domain_family") or ""),
        "compatible_promise_family": _promise_types_compatible(packet, sample),
        "similar_lived_scene": _text_similarity(
            str(packet.get("_lived_scene_family") or ""),
            str(sample.get("_lived_scene_family") or ""),
        ) >= 0.45,
        "overlapping_anchor_group": _overlap_ratio(packet.get("_anchor_ids") or [], sample.get("_anchor_ids") or []) >= 0.34,
        "repeated_support_overlap": _overlap_ratio(packet.get("_theme_tokens") or set(), sample.get("_theme_tokens") or set()) >= 0.22,
        "same_human_angle": _same_human_angle(packet, sample),
    }
    compatibility_count = sum(1 for matched in checks.values() if matched)
    score = 0.0
    if checks["same_domain_family"]:
        score += 0.24
    if checks["compatible_promise_family"]:
        score += 0.16
    if checks["similar_lived_scene"]:
        score += 0.18
    if checks["overlapping_anchor_group"]:
        score += 0.16
    if checks["repeated_support_overlap"]:
        score += 0.14
    if checks["same_human_angle"]:
        score += 0.12
    if compatibility_count < 2:
        score = min(score, 0.44)
    return min(1.0, score)


def _pick_cluster_main_packet(
    members: Sequence[Mapping[str, Any]],
    domain_family: str,
    focus_map: Sequence[DomainFocusScoreV1],
) -> Mapping[str, Any]:
    focus = _focus_score(domain_family, focus_map)
    best = None
    best_score = -1.0
    for packet in members:
        score = _safe_float(packet.get("strength"), 0.0) + (focus * 0.12) + _readability_bonus(packet)
        if packet.get("_is_auxiliary"):
            score -= 0.14
        if packet.get("_is_overlay"):
            score -= 0.08
        if score > best_score:
            best = packet
            best_score = score
    return best or members[0]


def _readability_bonus(packet: Mapping[str, Any]) -> float:
    subtype = str(packet.get("_subtype") or "")
    promise_type = str(packet.get("promise_type") or "")
    bonus = 0.0
    if subtype in {
        "affection_gift",
        "structured_originality",
        "internal_visibility_maturation",
        "self_construction",
        "attachment_architecture",
        "speech_decision_language",
        "warm_visibility_belonging",
        "roots_inner_security_transformation",
        "structured_imagination",
        "steady_public_drive",
        "freedom_responsibility_sensitivity",
        "social_emotional_intelligence",
        "home_security_roots",
        "public_voice_strategic_mind",
        "private_security_public_voice_axis",
        "action_through_balance",
        "action_restraint",
        "collective_identity",
        "harmony_wound_depth",
        "private_pressure",
    }:
        bonus += 0.12
    if promise_type in {"love_style", "mind_style", "career_signature", "identity_style", "social_mind_style", "creative_signature", "identity_action_style", "action_friction_to_strength", "emotional_home_signature", "career_mind_signature", "axis_tension", "collective_identity", "community_signature", "relationship_wound_to_gift", "career_love_style", "life_direction_axis"}:
        bonus += 0.08
    direct = str(packet.get("direct_meaning") or "")
    if 20 <= len(direct) <= 140:
        bonus += 0.04
    return bonus


def _cluster_label(packet: Mapping[str, Any]) -> str:
    subtype = str(packet.get("_subtype") or "").strip()
    if subtype:
        return subtype
    promise_family = str(packet.get("_promise_type_family") or "").strip()
    if promise_family:
        return promise_family
    return "core_theme"


def _cluster_id(domain_family: str, cluster_label: str, packet: Mapping[str, Any]) -> str:
    packet_id = str(packet.get("id") or "").strip()
    base = _normalize_text(cluster_label or packet_id or "cluster")
    packet_key = _normalize_text(packet_id or "packet")
    if base in {"gift_like", "mind_like", "career_like", "identity_like", "love_like", "generic", "wound_like", "shadow_like", "need_like", "action_like", "axis_like", "community_like"}:
        return f"{domain_family}_{base}_{packet_key}"
    return f"{domain_family}_{base}"


def _shared_themes(members: Sequence[Mapping[str, Any]]) -> list[str]:
    if not members:
        return []
    counts: dict[str, int] = defaultdict(int)
    for member in members:
        for token in member.get("_theme_tokens") or set():
            counts[str(token)] += 1
    items = [token for token, count in counts.items() if count >= max(1, min(2, len(members)))]
    items.sort()
    return items[:6]


def _add_cross_domain_memberships(
    *,
    clusters: list[NatalPromiseClusterV1],
    packets: Sequence[Mapping[str, Any]],
    focus_map: Sequence[DomainFocusScoreV1],
) -> None:
    packet_lookup = {str(packet.get("id") or ""): packet for packet in packets if str(packet.get("id") or "")}
    for cluster in clusters:
        members = [
            packet_lookup[member.packet_id]
            for member in cluster.packet_members
            if member.packet_id in packet_lookup
        ]
        seen_member_ids = {str(item.get("id") or "") for item in members}
        for packet in packets:
            packet_id = str(packet.get("id") or "")
            if not packet_id or packet_id in seen_member_ids:
                continue
            if _cross_domain_link_score(packet, cluster, focus_map) >= 0.45:
                members.append(packet)
                seen_member_ids.add(packet_id)
        unique_members = {str(item.get("id") or ""): item for item in members if str(item.get("id") or "")}
        _assign_member_roles(cluster, list(unique_members.values()))


def _assign_member_roles(cluster: NatalPromiseClusterV1, members: Sequence[Mapping[str, Any]]) -> None:
    cluster.packet_members = []
    main_packet = next(
        (member for member in members if str(member.get("id") or "") == cluster.main_packet_id),
        members[0] if members else {},
    )
    for member in members:
        packet_id = str(member.get("id") or "")
        subtype = str(member.get("_subtype") or "")
        if packet_id == cluster.main_packet_id:
            role: ClusterRole = "primary_anchor"
            contribution = "main_promise"
        else:
            role = _member_cluster_role(member=member, main_packet=main_packet)
            contribution = subtype or str(member.get("promise_type") or "support")
        cluster.packet_members.append(
            ClusterPacketMemberV1(
                packet_id=packet_id,
                cluster_role=role,
                contribution_type=contribution,
                source_type=str(member.get("source_type") or ""),
                reuse_anchor_ids=list(member.get("_anchor_ids") or []),
                explicit_anchor_allowed=True,
                reason=_member_reason(member, cluster),
                subtype=subtype,
            )
        )


def _member_cluster_role(
    *,
    member: Mapping[str, Any],
    main_packet: Mapping[str, Any],
) -> ClusterRole:
    if str(member.get("_subtype") or "") and str(member.get("_subtype") or "") != str(main_packet.get("_subtype") or ""):
        return "secondary_anchor"
    if _same_human_angle(member, main_packet):
        return "modifier"
    if _text_similarity(
        str(member.get("_lived_scene_family") or ""),
        str(main_packet.get("_lived_scene_family") or ""),
    ) < 0.4:
        return "secondary_anchor"
    if _overlap_ratio(member.get("_anchor_ids") or [], main_packet.get("_anchor_ids") or []) < 0.34:
        return "secondary_anchor"
    return "modifier"


def _member_reason(member: Mapping[str, Any], cluster: NatalPromiseClusterV1) -> str:
    if str(member.get("id") or "") == cluster.main_packet_id:
        return "main packet of cluster"
    if str(member.get("_subtype") or "") and str(member.get("_subtype") or "") not in cluster.subtypes[:1]:
        return "distinct subtype enriches cluster without duplicating main card"
    if str(member.get("_lived_scene_family") or "") and str(member.get("_lived_scene_family") or "") != cluster.distinct_lived_scene:
        return "distinct lived scene keeps a separate support angle"
    return "supports the cluster theme without taking over the main card"


def _cross_domain_link_score(
    packet: Mapping[str, Any],
    cluster: NatalPromiseClusterV1,
    focus_map: Sequence[DomainFocusScoreV1],
) -> float:
    packet_domain = str(packet.get("_domain_family") or "")
    if packet_domain == cluster.domain_family:
        return 1.0 if str(packet.get("id") or "") == cluster.main_packet_id else 0.0
    packet_id = str(packet.get("id") or "").lower()
    tokens = packet.get("_theme_tokens") or set()
    score = 0.0
    if "venus_sagittarius_12h" in packet_id and cluster.domain_family in {"career", "relationship"}:
        score += 0.6
    if "capricorn_asc" in packet_id and cluster.domain_family in {"mind", "career"}:
        score += 0.48
    if ("saturn_sextile_uranus" in packet_id or "saturn_3h" in packet_id) and cluster.domain_family in {"identity", "mind"}:
        score += 0.5
    if cluster.domain_family == "relationship" and tokens.intersection({"hidden", "love", "private", "meaning", "affection"}):
        score += 0.18
    if cluster.domain_family == "career" and tokens.intersection({"visibility", "creative", "creation", "production", "görünürlük"}):
        score += 0.18
    if cluster.domain_family == "identity" and tokens.intersection({"identity", "construction", "self", "public"}):
        score += 0.14
    if cluster.domain_family == "mind" and tokens.intersection({"mind", "zihin", "idea", "system", "speech", "decision"}):
        score += 0.14
    focus = _focus_score(cluster.domain_family, focus_map)
    score += focus * 0.08
    return min(1.0, score)


def _finalize_cluster_roles_and_mains(
    *,
    clusters: list[NatalPromiseClusterV1],
    focus_map: Sequence[DomainFocusScoreV1],
) -> None:
    for cluster in clusters:
        focus = _focus_score(cluster.domain_family, focus_map)
        main_member = next((member for member in cluster.packet_members if member.packet_id == cluster.main_packet_id), None)
        if main_member is None and cluster.packet_members:
            cluster.main_packet_id = cluster.packet_members[0].packet_id
            cluster.packet_members[0].cluster_role = "primary_anchor"
        cluster.cluster_strength = round(
            min(
                1.0,
                _safe_float(focus, 0.0) * 0.22
                + _cluster_member_strength(cluster) * 0.30
                + _cluster_role_diversity(cluster) * 0.08
                + _cluster_scene_coherence(cluster) * 0.10
                + _cluster_anchor_depth(cluster) * 0.08
                + _cluster_repeated_support(cluster) * 0.06
                + _cluster_main_readability(cluster) * 0.16,
            ),
            4,
        )
        cluster.public_card_priority = round(
            min(1.0, cluster.cluster_strength + _cluster_priority_bonus(cluster)),
            4,
        )
        cluster.source_type = _cluster_source_type(cluster)
        cluster.selection_notes = _cluster_selection_notes(cluster, focus)
        cluster.scoring_breakdown = {
            "focus_score": round(focus, 4),
            "member_strength": round(_cluster_member_strength(cluster), 4),
            "role_diversity": round(_cluster_role_diversity(cluster), 4),
            "scene_coherence": round(_cluster_scene_coherence(cluster), 4),
            "anchor_depth": round(_cluster_anchor_depth(cluster), 4),
            "repeated_support": round(_cluster_repeated_support(cluster), 4),
            "readability": round(_cluster_main_readability(cluster), 4),
        }


def _cluster_member_strength(cluster: NatalPromiseClusterV1) -> float:
    if not cluster.packet_members:
        return 0.0
    return min(1.0, len(cluster.packet_members) / 3.0)


def _cluster_role_diversity(cluster: NatalPromiseClusterV1) -> float:
    roles = {member.cluster_role for member in cluster.packet_members}
    return min(1.0, len(roles) / 3.0)


def _cluster_scene_coherence(cluster: NatalPromiseClusterV1) -> float:
    return 0.9 if cluster.distinct_lived_scene else 0.5


def _cluster_anchor_depth(cluster: NatalPromiseClusterV1) -> float:
    return min(1.0, len(cluster.technical_anchor_ids) / 4.0)


def _cluster_repeated_support(cluster: NatalPromiseClusterV1) -> float:
    return min(1.0, len(cluster.packet_members) / 3.0)


def _cluster_main_readability(cluster: NatalPromiseClusterV1) -> float:
    subtype_bonus = 0.2 if any(
        subtype in {
            "affection_gift",
            "structured_originality",
            "internal_visibility_maturation",
            "self_construction",
            "hidden_value_identity",
            "invisible_preparation",
            "trust_threshold_silent_desire",
            "inner_world_saturation",
            "deep_mind_pressure",
            "warm_visibility_belonging",
            "roots_inner_security_transformation",
            "structured_imagination",
            "steady_public_drive",
            "freedom_responsibility_sensitivity",
            "social_emotional_intelligence",
            "public_power_roots_tension",
            "home_security_roots",
            "public_voice_strategic_mind",
            "private_security_public_voice_axis",
            "action_through_balance",
            "action_restraint",
            "collective_identity",
            "harmony_wound_depth",
            "private_pressure",
        }
        for subtype in cluster.subtypes
    ) else 0.1
    return min(1.0, 0.6 + subtype_bonus)


def _cluster_priority_bonus(cluster: NatalPromiseClusterV1) -> float:
    bonus = 0.0
    if cluster.domain_family in {"identity", "mind", "relationship", "career", "inner_world", "home_family", "creativity", "action", "axis_tension", "community"}:
        bonus += 0.06
    if any(pt in {"mind_style", "mind_identity", "career_signature", "love_style", "identity_style", "social_mind_style", "creative_signature", "relationship_need", "identity_action_style", "action_friction_to_strength", "emotional_home_signature", "career_mind_signature", "axis_tension", "collective_identity", "community_signature", "relationship_wound_to_gift", "career_love_style", "life_direction_axis"} for pt in cluster.promise_types):
        bonus += 0.05
    if cluster.domain_family == "identity" and "self_construction" in cluster.subtypes:
        bonus += 0.04
    if cluster.domain_family == "inner_world" and "inner_world_saturation" in cluster.subtypes:
        bonus += 0.04
    if cluster.domain_family == "home_family" and "roots_inner_security_transformation" in cluster.subtypes:
        bonus += 0.05
    if cluster.domain_family == "creativity" and "structured_imagination" in cluster.subtypes:
        bonus += 0.05
    if cluster.domain_family == "career" and "steady_public_drive" in cluster.subtypes:
        bonus += 0.04
    if cluster.domain_family == "home_family" and "home_security_roots" in cluster.subtypes:
        bonus += 0.05
    if cluster.domain_family == "career" and "public_voice_strategic_mind" in cluster.subtypes:
        bonus += 0.05
    if cluster.domain_family == "axis_tension" and "private_security_public_voice_axis" in cluster.subtypes:
        bonus += 0.06
    if cluster.domain_family == "community" and "collective_identity" in cluster.subtypes:
        bonus += 0.04
    if cluster.domain_family == "relationship" and "harmony_wound_depth" in cluster.subtypes:
        bonus += 0.04
    return bonus


def _cluster_selection_notes(cluster: NatalPromiseClusterV1, focus: float) -> list[str]:
    notes: list[str] = []
    if focus >= 0.85:
        notes.append("strong focus-map domain")
    if cluster.domain_family in {"identity", "mind"}:
        notes.append("hero-capable cluster")
    if cluster.domain_family in {"home_family", "creativity"}:
        notes.append("v0.7/v0.8 domain coverage should survive fallback collapse")
    if cluster.domain_family in {"axis_tension", "action", "community"}:
        notes.append("v0.8 semantic coverage should survive generic fallback collapse")
    if "self_construction" in cluster.subtypes:
        notes.append("identity support should survive even if not hero")
    if len(cluster.packet_members) > 1:
        notes.append("has reusable sub-angles for detail")
    return notes


def _build_anchor_usage(clusters: Sequence[NatalPromiseClusterV1]) -> list[ClusterAnchorUsageV1]:
    usage: dict[str, ClusterAnchorUsageV1] = {}
    for cluster in clusters:
        for member in cluster.packet_members:
            for anchor_id in member.reuse_anchor_ids:
                state = usage.setdefault(anchor_id, ClusterAnchorUsageV1(anchor_id=anchor_id))
                if member.packet_id not in state.packet_ids:
                    state.packet_ids.append(member.packet_id)
                if cluster.id not in state.cluster_ids:
                    state.cluster_ids.append(cluster.id)
                if any(token in anchor_id for token in ("yukselen", "ascendant", "mc", "midheaven", "house:1", "house:10")):
                    state.chart_defining_override = True
    return list(usage.values())


def _build_surface_plan(
    *,
    clusters: Sequence[NatalPromiseClusterV1],
    focus_map: Sequence[DomainFocusScoreV1],
    anchor_usage: Sequence[ClusterAnchorUsageV1],
    packets: Sequence[Mapping[str, Any]],
) -> tuple[ClusterSurfacePlanV1, list[PacketSuppressionStateV1]]:
    sorted_clusters = sorted(clusters, key=lambda item: (-item.public_card_priority, item.id))
    packet_lookup = {str(item.get("id") or "").strip(): item for item in packets if str(item.get("id") or "").strip()}
    public_main: list[str] = []
    public_support: list[str] = []
    detail: list[str] = []
    domain_counts: dict[str, int] = defaultdict(int)
    family_counts: dict[str, int] = defaultdict(int)
    rejection_reasons: dict[str, str] = {}
    selected_lookup: dict[str, NatalPromiseClusterV1] = {}
    domain_lookup: dict[str, list[NatalPromiseClusterV1]] = defaultdict(list)
    public_main_target = _public_main_target(sorted_clusters)
    required_domains = _required_public_main_domains(sorted_clusters, focus_map)

    for cluster in sorted_clusters:
        domain_lookup[cluster.domain_family].append(cluster)

    def add_public_main(cluster: NatalPromiseClusterV1) -> None:
        family_key = _main_packet_family_key(cluster)
        cluster.target_surface_role = "public_main"
        public_main.append(cluster.id)
        domain_counts[cluster.domain_family] += 1
        if family_key:
            family_counts[family_key] += 1
        selected_lookup[cluster.id] = cluster

    for domain_family in required_domains:
        if len(public_main) >= public_main_target:
            break
        candidate = _preferred_domain_representative(domain_lookup.get(domain_family) or [])
        if candidate is None or candidate.id in selected_lookup:
            continue
        allowed, reason = _can_select_public_main(
            candidate,
            selected_lookup=selected_lookup,
            domain_lookup=domain_lookup,
            domain_counts=domain_counts,
            family_counts=family_counts,
            focus_map=focus_map,
            packet_lookup=packet_lookup,
            remaining_required_domains=[domain for domain in required_domains if domain_counts[domain] == 0 and domain != domain_family],
        )
        if allowed:
            add_public_main(candidate)
        else:
            rejection_reasons[candidate.id] = reason

    for cluster in sorted_clusters:
        if len(public_main) >= public_main_target:
            rejection_reasons.setdefault(cluster.id, "public_main_target_reached")
            continue
        if cluster.id in selected_lookup:
            continue
        remaining_required = [
            domain
            for domain in required_domains
            if domain_counts[domain] == 0 and domain != cluster.domain_family
        ]
        allowed, reason = _can_select_public_main(
            cluster,
            selected_lookup=selected_lookup,
            domain_lookup=domain_lookup,
            domain_counts=domain_counts,
            family_counts=family_counts,
            focus_map=focus_map,
            packet_lookup=packet_lookup,
            remaining_required_domains=remaining_required,
        )
        if not allowed:
            rejection_reasons[cluster.id] = reason
            continue
        add_public_main(cluster)

    for cluster in sorted_clusters:
        if cluster.id in public_main:
            continue
        focus = _focus_score(cluster.domain_family, focus_map)
        reason = rejection_reasons.get(cluster.id, "")
        if _prefer_detail_surface(cluster, reason=reason, domain_counts=domain_counts, focus_map=focus_map):
            cluster.target_surface_role = "detail"
            detail.append(cluster.id)
        elif focus >= 0.65 or (cluster.domain_family == "identity" and _identity_strong(focus_map)):
            cluster.target_surface_role = "public_support"
            public_support.append(cluster.id)
        else:
            cluster.target_surface_role = "detail"
            detail.append(cluster.id)

    if _identity_strong(focus_map):
        identity_clusters = [cluster for cluster in sorted_clusters if cluster.domain_family == "identity"]
        if identity_clusters and identity_clusters[0].id not in public_main and identity_clusters[0].id not in public_support:
            public_support.insert(0, identity_clusters[0].id)
            if identity_clusters[0].id in detail:
                detail.remove(identity_clusters[0].id)
            identity_clusters[0].target_surface_role = "public_support"

    packet_surfaces: dict[str, set[str]] = defaultdict(set)
    for cluster in sorted_clusters:
        role_name = cluster.target_surface_role
        for member in cluster.packet_members:
            packet_surfaces[member.packet_id].add(role_name)
            packet_surfaces[member.packet_id].add("debug")
            packet_surfaces[member.packet_id].add("transit_activation")
            if member.packet_id != cluster.main_packet_id:
                packet_surfaces[member.packet_id].add("detail")
            if member.cluster_role == "modifier":
                packet_surfaces[member.packet_id].add("modifier")
            if role_name != "public_main":
                packet_surfaces[member.packet_id].add("detail")

    suppressed: list[PacketSuppressionStateV1] = []
    for cluster in sorted_clusters:
        if cluster.id in public_main:
            continue
        reason = rejection_reasons.get(cluster.id, "")
        if not reason or reason == "public_main_target_reached":
            continue
        if reason in {"domain_saturation", "domain_public_main_cap"} and _distinct_from_selected_same_domain(cluster, selected_lookup):
            continue
        keep_for = ["detail", "debug", "transit_activation"]
        if cluster.target_surface_role == "public_support":
            keep_for.insert(0, "public_support")
        suppressed.append(
            PacketSuppressionStateV1(
                packet_id=cluster.main_packet_id,
                suppressed_from_public_main=True,
                keep_for=keep_for,
                reason=_public_main_rejection_reason(reason),
                superseded_by_cluster_id=_superseding_cluster_id(cluster, selected_lookup, packet_lookup),
            )
        )

    for cluster in sorted_clusters:
        main_packet = packet_lookup.get(cluster.main_packet_id) or {}
        for member in cluster.packet_members:
            packet_id = str(member.packet_id or "").strip()
            if not packet_id or packet_id == cluster.main_packet_id:
                continue
            packet = packet_lookup.get(packet_id) or {}
            if not _should_suppress_from_public_main(
                packet=packet,
                main_packet=main_packet,
                member=member,
                cluster=cluster,
            ):
                continue
            surfaces = packet_surfaces.get(packet_id) or set()
            keep_for = [item for item in ["detail", "modifier", "debug", "transit_activation"] if item in surfaces]
            suppressed.append(
                PacketSuppressionStateV1(
                    packet_id=packet_id,
                    suppressed_from_public_main=True,
                    keep_for=keep_for,
                    reason="weaker duplicate for the same domain card job and lived scene",
                    superseded_by_cluster_id=cluster.id,
                    superseded_by_packet_id=cluster.main_packet_id,
                )
            )

    _apply_anchor_budget(public_main, sorted_clusters, anchor_usage)

    return (
        ClusterSurfacePlanV1(
            public_main_cluster_ids=public_main[:PUBLIC_MAIN_MAX],
            public_support_cluster_ids=public_support,
            detail_cluster_ids=detail[: max(DEFAULT_DETAIL_TARGET, len(detail))],
            debug_packet_ids=sorted(packet_surfaces.keys()),
        ),
        suppressed,
    )


def _public_main_target(clusters: Sequence[NatalPromiseClusterV1]) -> int:
    if len(clusters) <= DEFAULT_PUBLIC_MAIN_MIN:
        return min(PUBLIC_MAIN_MAX, len(clusters))
    return min(PUBLIC_MAIN_MAX, max(DEFAULT_PUBLIC_MAIN_MIN, min(DEFAULT_PUBLIC_MAIN_TARGET, len(clusters))))


def _required_public_main_domains(
    clusters: Sequence[NatalPromiseClusterV1],
    focus_map: Sequence[DomainFocusScoreV1],
) -> list[str]:
    grouped: dict[str, list[NatalPromiseClusterV1]] = defaultdict(list)
    for cluster in clusters:
        grouped[cluster.domain_family].append(cluster)
    required: list[str] = []
    for domain_family, domain_clusters in grouped.items():
        focus = _focus_score(domain_family, focus_map)
        subtype_count = len({_cluster_semantic_key(cluster) for cluster in domain_clusters if _cluster_semantic_key(cluster)})
        threshold = 0.65
        if domain_family == "relationship" and subtype_count >= 2:
            threshold = 0.45
        if focus >= threshold and subtype_count >= 2:
            required.append(domain_family)
    required.sort(key=lambda item: (-_focus_score(item, focus_map), item))
    return required


def _preferred_domain_representative(clusters: Sequence[NatalPromiseClusterV1]) -> NatalPromiseClusterV1 | None:
    if not clusters:
        return None
    ordered = sorted(
        clusters,
        key=lambda item: (
            _domain_preference_rank(item),
            -item.public_card_priority,
            item.id,
        ),
    )
    return ordered[0]


def _domain_preference_rank(cluster: NatalPromiseClusterV1) -> tuple[int, float]:
    semantic_key = _cluster_semantic_key(cluster)
    preference_map = {
        "relationship": {
            "harmony_wound_depth": 0,
            "public_love_responsibility": 1,
            "attachment_architecture": 0,
            "freedom_responsibility_sensitivity": 1,
            "trust_threshold_silent_desire": 2,
            "trust_bond": 3,
            "affection_gift": 4,
            "private_love_inner_beauty": 5,
            "relationship_power_depth": 6,
            "hidden_romantic_pride": 7,
            "attraction_signal": 8,
            "emotional_routine_sensitivity": 9,
            "hidden_private_love_pattern": 10,
        },
        "mind": {
            "structured_originality": 0,
            "social_emotional_intelligence": 1,
            "speech_decision_language": 2,
            "deep_mind_pressure": 3,
            "deep_speech_psychological_learning": 4,
            "social_intuition_mind": 5,
            "big_mind": 6,
        },
        "identity": {
            "hidden_value_identity": 0,
            "warm_visibility_belonging": 1,
            "self_construction": 2,
            "soft_hidden_magnetism": 3,
            "visible_sensitivity_self_correction": 4,
            "unsettled_outer_signal": 5,
            "deep_resilience": 6,
        },
        "career": {
            "public_voice_strategic_mind": 0,
            "public_style_responsibility": 1,
            "steady_public_drive": 0,
            "invisible_preparation": 1,
            "public_power_roots_tension": 2,
            "internal_visibility_maturation": 3,
            "healing_voice": 4,
        },
        "inner_world": {
            "private_pressure": 0,
            "inner_world_saturation": 0,
            "private_maturity": 1,
            "private_will_hidden_drive": 2,
            "hidden_action_soft_drive": 3,
        },
        "home_family": {
            "home_security_roots": 0,
            "roots_inner_security_transformation": 0,
            "private_emotional_inheritance": 1,
        },
        "action": {
            "action_through_balance": 0,
            "action_restraint": 1,
        },
        "axis_tension": {
            "private_security_public_voice_axis": 0,
            "service_action_axis": 1,
        },
        "community": {
            "collective_identity": 0,
            "future_collective_signal": 1,
        },
        "creativity": {
            "structured_imagination": 0,
            "serious_heart_creative_form": 1,
        },
    }
    rank = preference_map.get(cluster.domain_family, {}).get(semantic_key, 2 if semantic_key else 3)
    generic_penalty = 0.2 if _is_generic_cluster(cluster) else 0.0
    return rank, generic_penalty


def _can_select_public_main(
    cluster: NatalPromiseClusterV1,
    *,
    selected_lookup: Mapping[str, NatalPromiseClusterV1],
    domain_lookup: Mapping[str, Sequence[NatalPromiseClusterV1]],
    domain_counts: Mapping[str, int],
    family_counts: Mapping[str, int],
    focus_map: Sequence[DomainFocusScoreV1],
    packet_lookup: Mapping[str, Mapping[str, Any]],
    remaining_required_domains: Sequence[str],
) -> tuple[bool, str]:
    focus = _focus_score(cluster.domain_family, focus_map)
    semantic_key = _cluster_semantic_key(cluster)
    family_key = _main_packet_family_key(cluster)
    if (
        cluster.domain_family == "relationship"
        and _is_generic_cluster(cluster)
        and _has_specific_relationship_public_alternative(cluster, domain_lookup=domain_lookup)
    ):
        return False, "relationship_generic_prefers_specific_subtype"
    if family_key and family_counts.get(family_key, 0) > 0:
        other = next(
            (
                item
                for item in selected_lookup.values()
                if _main_packet_family_key(item) == family_key
            ),
            None,
        )
        if other is None or not _materially_distinct_public_job(cluster, other):
            return False, "same_signal_family_already_in_public_main"
    if cluster.domain_family == "relationship" and semantic_key == "hidden_private_love_pattern":
        top_domain = max(focus_map, key=lambda item: item.score).domain if focus_map else ""
        if top_domain != "relationship" or domain_counts.get("relationship", 0) > 0:
            return False, "relationship_hidden_private_prefers_support"
    if domain_counts.get(cluster.domain_family, 0) >= 2:
        return False, "domain_public_main_cap"
    if domain_counts.get(cluster.domain_family, 0) >= 1:
        if remaining_required_domains:
            return False, "reserve_slot_for_unrepresented_domain"
        if not _allows_second_public_main(cluster, focus=focus, packet_lookup=packet_lookup):
            return False, "domain_saturation"
    if _is_generic_cluster(cluster) and focus < 0.85 and domain_counts.get(cluster.domain_family, 0) > 0:
        return False, "generic_repeat_prefers_support"
    return True, ""


def _allows_second_public_main(
    cluster: NatalPromiseClusterV1,
    *,
    focus: float,
    packet_lookup: Mapping[str, Mapping[str, Any]],
) -> bool:
    if focus < 0.85:
        return False
    semantic_key = _cluster_semantic_key(cluster)
    if cluster.domain_family == "career":
        return semantic_key in {"steady_public_drive", "public_power_roots_tension", "internal_visibility_maturation", "healing_voice"}
    if cluster.domain_family == "identity":
        return semantic_key in {"warm_visibility_belonging", "self_construction", "deep_resilience"} or _cluster_has_pressure_signature(cluster, packet_lookup=packet_lookup)
    if cluster.domain_family == "mind":
        return semantic_key in {"structured_originality", "social_emotional_intelligence", "speech_decision_language", "big_mind"} and not _is_generic_cluster(cluster)
    if cluster.domain_family == "home_family":
        return semantic_key in {"roots_inner_security_transformation", "private_emotional_inheritance"} and not _is_generic_cluster(cluster)
    if cluster.domain_family == "creativity":
        return semantic_key in {"structured_imagination", "serious_heart_creative_form"} and not _is_generic_cluster(cluster)
    return not _is_generic_cluster(cluster)


def _prefer_detail_surface(
    cluster: NatalPromiseClusterV1,
    *,
    reason: str,
    domain_counts: Mapping[str, int],
    focus_map: Sequence[DomainFocusScoreV1],
) -> bool:
    semantic_key = _cluster_semantic_key(cluster)
    if reason in {
        "same_signal_family_already_in_public_main",
        "domain_saturation",
        "domain_public_main_cap",
        "generic_repeat_prefers_support",
    }:
        return True
    if reason == "relationship_hidden_private_prefers_support" and domain_counts.get("relationship", 0) > 0:
        return True
    if cluster.domain_family == "relationship" and semantic_key == "hidden_private_love_pattern":
        top_domain = max(focus_map, key=lambda item: item.score).domain if focus_map else ""
        return top_domain != "relationship"
    return False


def _public_main_rejection_reason(reason: str) -> str:
    mapping = {
        "same_signal_family_already_in_public_main": "same signal family already has a stronger public-main cluster",
        "relationship_generic_prefers_specific_subtype": "generic relationship cluster stayed below a more specific relationship subtype",
        "relationship_hidden_private_prefers_support": "hidden/private love pattern stays support-detail unless relationship dominates the chart",
        "domain_saturation": "domain already has a stronger public-main representative",
        "domain_public_main_cap": "domain already reached the public-main diversity cap",
        "reserve_slot_for_unrepresented_domain": "public-main slot was held for an unrepresented strong domain",
        "generic_repeat_prefers_support": "generic repeat cluster was kept below subtype-led public-main cards",
        "public_main_target_reached": "public-main target was reached before this cluster",
    }
    return mapping.get(reason, "cluster stayed out of public-main after diversity filtering")


def _superseding_cluster_id(
    cluster: NatalPromiseClusterV1,
    selected_lookup: Mapping[str, NatalPromiseClusterV1],
    packet_lookup: Mapping[str, Mapping[str, Any]],
) -> str | None:
    family_key = _main_packet_family_key(cluster)
    if family_key:
        for selected in selected_lookup.values():
            if _main_packet_family_key(selected) == family_key:
                return selected.id
    same_domain = [item for item in selected_lookup.values() if item.domain_family == cluster.domain_family]
    if not same_domain:
        return None
    same_domain.sort(key=lambda item: (-item.public_card_priority, item.id))
    return same_domain[0].id


def _distinct_from_selected_same_domain(
    cluster: NatalPromiseClusterV1,
    selected_lookup: Mapping[str, NatalPromiseClusterV1],
) -> bool:
    same_domain = [item for item in selected_lookup.values() if item.domain_family == cluster.domain_family]
    if not same_domain:
        return False
    semantic_key = _cluster_semantic_key(cluster)
    for selected in same_domain:
        if _main_packet_family_key(selected) == _main_packet_family_key(cluster):
            return False
        if semantic_key and semantic_key == _cluster_semantic_key(selected):
            return False
        if any(promise in selected.promise_types for promise in cluster.promise_types) and _text_similarity(
            _fingerprint_text(cluster.distinct_lived_scene, limit=8),
            _fingerprint_text(selected.distinct_lived_scene, limit=8),
        ) >= 0.45:
            return False
    return True


def _cluster_allows_domain_repeat(cluster: NatalPromiseClusterV1) -> bool:
    if len(set(cluster.promise_types)) > 1:
        return True
    if len(cluster.subtypes) > 1:
        return True
    return any(member.cluster_role != "modifier" for member in cluster.packet_members[1:])


def _cluster_semantic_key(cluster: NatalPromiseClusterV1) -> str:
    for subtype in cluster.subtypes:
        clean = str(subtype or "").strip()
        if clean:
            return clean
    packet_id = str(cluster.main_packet_id or "")
    if "deep_resilience" in packet_id:
        return "deep_resilience"
    if "big_mind" in packet_id:
        return "big_mind"
    if "speech_decision_language" in packet_id:
        return "speech_decision_language"
    if "structured_originality" in packet_id:
        return "structured_originality"
    if "home_security_roots" in packet_id or "moon_cancer_ic" in packet_id:
        return "home_security_roots"
    if "public_voice_strategic_mind" in packet_id or "mercury_capricorn_mc" in packet_id:
        return "public_voice_strategic_mind"
    if "private_security_public_voice_axis" in packet_id or "moon_mercury_ic_mc" in packet_id:
        return "private_security_public_voice_axis"
    if "action_through_balance" in packet_id or "aries_asc_mars_libra_6h" in packet_id:
        return "action_through_balance"
    if "action_restraint" in packet_id or "mars_opposite_saturn" in packet_id:
        return "action_restraint"
    if "private_pressure_hidden_self_control" in packet_id or "saturn_aries_12h" in packet_id:
        return "private_pressure"
    if "collective_identity" in packet_id or "sun_aquarius_11h" in packet_id:
        return "collective_identity"
    if "future_collective_signal" in packet_id or "aquarius_11h" in packet_id:
        return "future_collective_signal"
    if "public_style_responsibility" in packet_id or "capricorn_10h_mercury_venus_neptune" in packet_id:
        return "public_style_responsibility"
    if "harmony_wound_depth" in packet_id or "libra_dsc_chiron_scorpio_7h" in packet_id:
        return "harmony_wound_depth"
    if "public_love_style_responsibility" in packet_id or "venus_capricorn_10h" in packet_id:
        return "public_love_responsibility"
    if "service_action_axis" in packet_id or "libra_aries_6h_12h" in packet_id:
        return "service_action_axis"
    if "self_construction" in packet_id:
        return "self_construction"
    if "trust_bond" in packet_id or "venus_trine_saturn" in packet_id:
        return "trust_bond"
    if "trust_threshold_silent_desire" in packet_id or "dsc_scorpio_ruler_mars_pisces_12h" in packet_id:
        return "trust_threshold_silent_desire"
    if "freedom_responsibility_sensitivity" in packet_id or "aquarius_dsc_saturn_pisces_7h" in packet_id:
        return "freedom_responsibility_sensitivity"
    if "hidden_romantic_pride" in packet_id or "venus_leo_12h" in packet_id:
        return "hidden_romantic_pride"
    if "attraction_signal" in packet_id or "venus_trine_mars" in packet_id:
        return "attraction_signal"
    if "emotional_routine_sensitivity" in packet_id or "moon_scorpio_6h" in packet_id:
        return "emotional_routine_sensitivity"
    if "private_love_inner_beauty" in packet_id or "venus_taurus_12h" in packet_id:
        return "private_love_inner_beauty"
    if "relationship_power_depth" in packet_id or "pluto_7h" in packet_id:
        return "relationship_power_depth"
    if "hidden_expansive_love" in packet_id:
        return "hidden_private_love_pattern" if cluster.domain_family == "relationship" else "internal_visibility_maturation"
    if "invisible_preparation" in packet_id or "mc_capricorn_ruler_saturn_pisces_12h" in packet_id:
        return "invisible_preparation"
    if "steady_public_drive" in packet_id or "mc_taurus_mars_10h" in packet_id:
        return "steady_public_drive"
    if "public_power_roots_tension" in packet_id or "mars_opposite_pluto" in packet_id:
        return "public_power_roots_tension"
    if "hidden_value_identity" in packet_id or "taurus_asc_venus_12h" in packet_id:
        return "hidden_value_identity"
    if "warm_visibility_belonging" in packet_id or "leo_asc_sun_cancer_11h" in packet_id:
        return "warm_visibility_belonging"
    if "visible_sensitivity_self_correction" in packet_id or "chiron_virgo_1h" in packet_id:
        return "visible_sensitivity_self_correction"
    if "soft_hidden_magnetism" in packet_id or "venus_12h_conjunct_asc" in packet_id:
        return "soft_hidden_magnetism"
    if "unsettled_outer_signal" in packet_id or "uranus_square_asc_venus" in packet_id:
        return "unsettled_outer_signal"
    if "social_intuition_mind" in packet_id or "mercury_pisces_11h" in packet_id:
        return "social_intuition_mind"
    if "social_emotional_intelligence" in packet_id or "sun_mercury_cancer_11h" in packet_id:
        return "social_emotional_intelligence"
    if "deep_speech_psychological_learning" in packet_id or "jupiter_scorpio_3h" in packet_id:
        return "deep_speech_psychological_learning"
    if "deep_mind_pressure" in packet_id or "mercury_square_pluto" in packet_id:
        return "deep_mind_pressure"
    if "roots_inner_security_transformation" in packet_id or "pluto_node_scorpio_4h" in packet_id:
        return "roots_inner_security_transformation"
    if "private_emotional_inheritance" in packet_id or "ic_scorpio_pluto_node" in packet_id:
        return "private_emotional_inheritance"
    if "structured_imagination" in packet_id or "moon_uranus_neptune_capricorn_5h" in packet_id:
        return "structured_imagination"
    if "serious_heart_creative_form" in packet_id or "moon_capricorn_5h" in packet_id:
        return "serious_heart_creative_form"
    if "inner_world_saturation" in packet_id or "pisces_12h_stellium" in packet_id:
        return "inner_world_saturation"
    if "private_maturity_boundary_sensitivity" in packet_id or "saturn_pisces_12h" in packet_id:
        return "private_maturity"
    if "hidden_action_soft_drive" in packet_id or "mars_pisces_12h" in packet_id:
        return "hidden_action_soft_drive"
    if "private_will_and_hidden_drive" in packet_id or "sun_mars_pisces_12h" in packet_id:
        return "private_will_hidden_drive"
    return ""


def _has_specific_relationship_public_alternative(
    cluster: NatalPromiseClusterV1,
    *,
    domain_lookup: Mapping[str, Sequence[NatalPromiseClusterV1]],
) -> bool:
    if cluster.domain_family != "relationship":
        return False
    siblings = domain_lookup.get("relationship") or []
    specific_siblings = [
        item
        for item in siblings
        if item.id != cluster.id and not _is_generic_cluster(item) and _cluster_semantic_key(item)
    ]
    if len(specific_siblings) < 2:
        return False
    best_specific = max(specific_siblings, key=lambda item: (item.public_card_priority, item.cluster_strength, item.id))
    return best_specific.public_card_priority >= (cluster.public_card_priority - 0.08)


def _is_generic_cluster(cluster: NatalPromiseClusterV1) -> bool:
    return cluster.cluster_label in {
        "gift_like",
        "mind_like",
        "career_like",
        "identity_like",
        "love_like",
        "generic",
        "wound_like",
        "shadow_like",
        "need_like",
        "action_like",
        "axis_like",
        "community_like",
    } and not any(str(item or "").strip() for item in cluster.subtypes)


def _cluster_source_type(cluster: NatalPromiseClusterV1) -> str:
    if _is_generic_cluster(cluster):
        return "generic_fallback"
    main_member = next(
        (member for member in cluster.packet_members if member.packet_id == cluster.main_packet_id),
        None,
    )
    source_type = str((main_member.source_type if main_member is not None else "") or "").strip()
    if source_type in {"exact_registry", "composed_semantic", "generic_fallback", "discovery_scaffold", "legacy_graph"}:
        return source_type
    return "legacy_graph"


def _empty_source_type_distribution() -> dict[str, int]:
    return {
        "exact_registry": 0,
        "composed_semantic": 0,
        "generic_fallback": 0,
        "discovery_scaffold": 0,
        "legacy_graph": 0,
    }


def _packet_source_type_distribution(candidate_packets: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = _empty_source_type_distribution()
    for packet in candidate_packets:
        source_type = str(packet.get("source_type") or "").strip()
        if source_type in counts:
            counts[source_type] += 1
    return counts


def _cluster_source_type_distribution(
    *,
    clusters: Sequence[NatalPromiseClusterV1],
    cluster_ids: Sequence[str],
) -> dict[str, int]:
    counts = _empty_source_type_distribution()
    cluster_lookup = {cluster.id: cluster for cluster in clusters}
    for cluster_id in cluster_ids:
        cluster = cluster_lookup.get(str(cluster_id or "").strip())
        if cluster is None:
            continue
        source_type = str(cluster.source_type or "").strip()
        if source_type in counts:
            counts[source_type] += 1
    return counts


def _main_packet_family_key(cluster: NatalPromiseClusterV1) -> str:
    packet_id = str(cluster.main_packet_id or "").strip()
    clean = re.sub(r"_(identity|relationship|career|mind)_chart_exact$", "", packet_id)
    clean = re.sub(r"_chart_exact$", "", clean)
    clean = re.sub(r"_(identity|relationship|career|mind)$", "", clean)
    return clean


def _materially_distinct_public_job(left: NatalPromiseClusterV1, right: NatalPromiseClusterV1) -> bool:
    if left.domain_family == right.domain_family:
        return False
    if _cluster_semantic_key(left) == _cluster_semantic_key(right):
        return False
    scene_similarity = _text_similarity(
        _fingerprint_text(left.distinct_lived_scene, limit=8),
        _fingerprint_text(right.distinct_lived_scene, limit=8),
    )
    return scene_similarity < 0.28


def _cluster_has_pressure_signature(
    cluster: NatalPromiseClusterV1,
    *,
    packet_lookup: Mapping[str, Mapping[str, Any]],
) -> bool:
    packet = packet_lookup.get(cluster.main_packet_id) or {}
    text = " ".join(
        [
            str(cluster.main_packet_id or ""),
            " ".join(cluster.technical_anchor_ids),
            " ".join(str(item).strip() for item in (packet.get("technical_anchors") or []) if str(item).strip()),
        ]
    ).lower()
    return any(token in text for token in ("resilience", "pressure", "saturn trine pluto", "sun square saturn", "mars opposite saturn", "mars opposition saturn"))


def _should_suppress_from_public_main(
    *,
    packet: Mapping[str, Any],
    main_packet: Mapping[str, Any],
    member: ClusterPacketMemberV1,
    cluster: NatalPromiseClusterV1,
) -> bool:
    if member.cluster_role == "primary_anchor":
        return False
    if str(packet.get("_domain_family") or cluster.domain_family) != cluster.domain_family:
        return False
    if str(packet.get("_promise_type_family") or "") != str(main_packet.get("_promise_type_family") or ""):
        return False
    if str(packet.get("_lived_scene_family") or "") != str(main_packet.get("_lived_scene_family") or ""):
        return False
    if str(packet.get("_subtype") or "") and str(packet.get("_subtype") or "") != str(main_packet.get("_subtype") or ""):
        return False
    if str(packet.get("_anchor_group_fingerprint") or "") != str(main_packet.get("_anchor_group_fingerprint") or ""):
        return False
    if member.cluster_role != "modifier":
        return False
    return _readability_bonus(packet) <= _readability_bonus(main_packet)


def _identity_strong(focus_map: Sequence[DomainFocusScoreV1]) -> bool:
    return _focus_score("identity", focus_map) >= 0.65


def _apply_anchor_budget(
    public_main_cluster_ids: Sequence[str],
    clusters: Sequence[NatalPromiseClusterV1],
    anchor_usage: Sequence[ClusterAnchorUsageV1],
) -> None:
    usage_lookup = {item.anchor_id: item for item in anchor_usage}
    cluster_lookup = {cluster.id: cluster for cluster in clusters}
    explicit_counts: dict[str, int] = defaultdict(int)
    for cluster_id in public_main_cluster_ids:
        cluster = cluster_lookup.get(cluster_id)
        if cluster is None:
            continue
        for member in cluster.packet_members:
            if member.packet_id != cluster.main_packet_id:
                member.explicit_anchor_allowed = True
                continue
            allow = True
            for anchor_id in member.reuse_anchor_ids:
                state = usage_lookup.get(anchor_id)
                if state is None:
                    continue
                if explicit_counts[anchor_id] >= state.explicit_use_budget and not state.chart_defining_override:
                    allow = False
                    state.public_main_explicit_uses = min(explicit_counts[anchor_id], state.explicit_use_budget)
                    continue
                explicit_counts[anchor_id] += 1
                state.public_main_explicit_uses = explicit_counts[anchor_id]
            member.explicit_anchor_allowed = allow


def _focus_score(domain_family: str, focus_map: Sequence[DomainFocusScoreV1]) -> float:
    for item in focus_map:
        if item.domain == domain_family:
            return item.score
    return 0.0


def _promise_types_compatible(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    left_family = str(left.get("_promise_type_family") or "")
    right_family = str(right.get("_promise_type_family") or "")
    if left_family == right_family:
        return True
    compatible_pairs = {
        ("gift_like", "love_like"),
        ("gift_like", "mind_like"),
        ("identity_like", "mind_like"),
        ("career_like", "wound_like"),
    }
    return (left_family, right_family) in compatible_pairs or (right_family, left_family) in compatible_pairs


def _same_human_angle(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    if str(left.get("_subtype") or "") and str(left.get("_subtype") or "") == str(right.get("_subtype") or ""):
        return True
    return _text_similarity(
        str(left.get("_human_angle_fingerprint") or ""),
        str(right.get("_human_angle_fingerprint") or ""),
    ) >= 0.34


def _base_packet_id(packet: Mapping[str, Any]) -> str:
    packet_id = str(packet.get("id") or "").strip()
    for suffix in ("_aux", "_identity_overlay", "_behavior_reflex_overlay", "_career_overlay"):
        if packet_id.endswith(suffix):
            return packet_id[: -len(suffix)]
    return packet_id


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_text(text: str) -> str:
    clean = str(text or "").lower().strip()
    clean = clean.replace("ı", "i").replace("İ", "i")
    clean = clean.replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    clean = re.sub(r"[^a-z0-9\s:_\-]", " ", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _fingerprint_text(text: str, *, limit: int) -> str:
    tokens = _tokenize(text)
    return " ".join(tokens[:limit]).strip()


def _tokenize(text: str) -> list[str]:
    clean = _normalize_text(text)
    return [token for token in clean.split() if token]


def _text_similarity(left: str, right: str) -> float:
    left_tokens = set(_tokenize(left))
    right_tokens = set(_tokenize(right))
    return _overlap_ratio(left_tokens, right_tokens)


def _overlap_ratio(left: Sequence[str] | set[str], right: Sequence[str] | set[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set or not right_set:
        return 0.0
    return len(left_set.intersection(right_set)) / float(len(left_set.union(right_set)))


def _unique_strings(values: Sequence[str] | Any) -> list[str]:
    out: list[str] = []
    for value in values:
        clean = str(value or "").strip()
        if clean and clean not in out:
            out.append(clean)
    return out
