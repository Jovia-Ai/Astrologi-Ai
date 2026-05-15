# Natal Compositional Grammar v0.9 Implementation Spec

## 1. Purpose

This document turns the accepted compositional grammar plan into a concrete `v0.9` implementation spec.

This is still a planning artifact only.

Hard constraints:
- do not implement code yet
- do not change runtime
- do not add registry entries
- do not touch renderer
- do not change public output

`v0.9` scope is limited to four core route families:
- `identity_route`
- `relationship_route`
- `career_route`
- `moon_signature`

Out of scope for this spec:
- `2H/8H`
- `3H/9H`
- `4H/IC`
- `5H`
- `12H`
- tight-aspect special families
- renderer-side public copy generation
- registry expansion

## 2. Decision Summary

The `50`-chart audit already established the ordering:
- discovery is working
- generic fallback still owns too many `public_main` slots
- discovery scaffolds do not yet become semantic candidates that ClusterPlan can safely use

Therefore `v0.9` should add a grammar layer that:
- builds composed candidates from primitive chart facts and discovery routes
- keeps them traceable and chart-fact safe
- exposes them to ClusterPlan without letting them auto-own public surfaces
- lets exact registry remain the strongest trusted semantic memory

Core rule:

`exact_registry > composed_semantic > raw_generic_fallback > discovery_scaffold`

But exact registry should win only when domain context and `public_job` are compatible.

Additional rollout decision for `v0.9a`:
- phase 1 must be a public-output no-op
- only `identity_route` and `career_route` are in scope
- `relationship_route` and `moon_signature` remain `v0.9b`

## 3. Current Integration Context

Current chain in the repo:

```text
build_public_natal_view(...)
  -> build_natal_promise_packets_v1(...)
  -> build_natal_promise_packets_v1(..., mode="candidate_inventory")
  -> build_natal_promise_cluster_plan_v1(...)
  -> build_profile_narrative_projection_v1(...)
  -> build_profile_v8_projection_v1(...)
```

Current observations from code:
- `backend/app/natal/natal_promise_packets.py` already produces:
  - exact registry-derived packets
  - chart-signature packets
  - `v0.6` discovery scaffolds
  - `source_type` tagging
- `backend/app/natal/natal_promise_cluster_plan.py` already computes:
  - `focus_map`
  - `clusters`
  - `surface_plan`
  - `coverage_warnings`
  - `audit_metrics`
  - `source_type` distributions
- `backend/app/natal/public_builder.py` already builds:
  - `selected` packet output
  - `candidate_inventory`
  - ClusterPlan input/output

This means `v0.9` does not need a new architecture. It needs a new candidate layer inserted into the existing one.

## 4. Proposed Data Models

## 4.1 `ComposedSemanticCandidateV1`

Proposed dataclass shape:

```python
@dataclass
class ComposedSemanticCandidateV1:
    id: str
    family: str
    subtype: str
    source_type: str  # always "composed_semantic"
    domain: str
    domain_reason: list[str]
    public_job: str
    confidence: float
    confidence_tier: str  # low | medium | high
    chart_facts_match: bool
    technical_anchors: list[str]
    source_evidence_ids: list[str]
    evidence_trace: dict[str, Any]
    direct_meaning: str
    lived_scene: str
    lived_scene_atoms: list[str]
    gift: str
    inner_tension: str
    growth_direction: str
    avoid_readings: list[str]
    projection_hints: dict[str, Any]
    scoring_breakdown: dict[str, float]
    matched_archetypes: list[str]
    override_eligible: bool
    public_eligibility: dict[str, Any]
    meta: dict[str, Any]
```

Notes:
- the shape intentionally mirrors existing packet dictionaries so integration is low-risk
- this is not a new public schema
- this is an internal planning model for packet construction and cluster selection

## 4.2 `public_eligibility` subshape

```python
{
    "debug_eligible": bool,
    "detail_eligible": bool,
    "public_support_eligible": bool,
    "public_main_eligible": bool,
    "reason_codes": list[str],
}
```

Initial rollout target:
- `debug_eligible = true`
- `detail_eligible = true` when confidence is at least medium
- `public_support_eligible = true` when confidence is at least medium and scene evidence exists
- `public_main_eligible = false` by default in `v0.9`

## 4.3 `evidence_trace` subshape

```python
{
    "primitive_facts": {
        "placements": [...],
        "aspects": [...],
        "angles": [...],
        "houses": [...],
    },
    "discovery_routes": [...],
    "family_inputs": [...],
    "subtype_inputs": [...],
    "contradictions": [...],
    "registry_override_considered": [...],
}
```

This is required because composed candidates must remain auditable.

## 5. Build Pipeline

## 5.1 Primitive Astro Facts -> Discovery -> Composed Candidates

The implementation should not bypass `v0.6` discovery.

Required build order:

```text
primitive astro facts
  -> discovery route flags
  -> composed family builder
  -> candidate packet normalization
  -> ClusterPlan eligibility / ranking
```

`v0.9` builders should consume:
- `planets`
- `aspects`
- `natal_graph_compact`
- `metadata`
- `meta_info`
- already-existing discovery hints from `candidate_inventory`

## 5.2 Candidate production rule

For each of the four route families:
- if discovery route is absent or clearly weak, do not emit a composed candidate
- if discovery route is present but too abstract, emit debug-only
- if route is present with enough scene support, emit debug/detail/public_support candidate
- do not emit `public_main` eligibility by default

## 5.3 Semantic ingredients, not final prose

Composed candidate fields are semantic ingredients, not polished public copy.

Fields such as:
- `direct_meaning`
- `lived_scene`
- `gift`
- `inner_tension`
- `growth_direction`

should be concise semantic material for ClusterPlan and later renderer use.

They should not be treated as:
- final public wording
- release-ready prose blocks
- renderer replacement text

Renderer remains responsible for final wording. `v0.9a` only adds structured semantic material.

## 6. Route Family Specs

## 6.1 `identity_route`

### Inputs
- `ASC`
- chart ruler
- Sun
- `1H` planets
- angularity
- ASC aspects if available
- chart spine if available

### Candidate construction
- start from ASC sign tone as entry style
- route through chart ruler sign + house + angularity
- add Sun as core vitality and self-construction modifier
- add `1H` amplification if present
- build one primary subtype and at most one secondary subtype

### Candidate subtypes
- `direct_identity_spine`
- `mediated_identity_spine`
- `controlled_identity_spine`
- `relational_identity_spine`
- `private_identity_spine`

### Confidence scoring

Suggested scoring components:
- `asc_strength`: `0.0 - 0.25`
- `chart_ruler_strength`: `0.0 - 0.30`
- `sun_alignment_strength`: `0.0 - 0.20`
- `first_house_amplification`: `0.0 - 0.10`
- `angularity_bonus`: `0.0 - 0.10`
- `coherence_bonus`: `0.0 - 0.05`

Reduce score when:
- Sun strongly belongs to another route family
- chart ruler conflicts without coherent lived scene

### `domain_reason`

Examples:
- `ASC route`
- `chart ruler route`
- `Sun identity anchor`
- `1H amplification`
- `angular identity emphasis`

### `public_job`

Allowed values in first rollout:
- `main_identity`
- `support_gift`
- `detail_shadow`
- `debug_only`

### Exact registry override

Registry wins only when:
- chart facts match
- registry packet is identity-domain compatible
- `public_job` matches
- registry packet is more specific than the composed route

### Generic fallback suppression

Composed identity can beat raw generic identity fallback only when:
- chart-fact safe
- confidence >= medium
- `lived_scene` present
- `domain_reason` explicit
- no stronger exact registry packet exists

### Public eligibility

Default `v0.9`:
- debug: yes
- detail: yes if confidence >= medium
- support: yes if confidence >= medium and lived scene exists
- public_main: no by default

## 6.2 `relationship_route`

### Inputs
- `DSC`
- DSC ruler
- Venus
- Mars
- Moon
- `5H / 7H / 8H` links
- Venus / Mars / Moon aspects
- relationship contradictions if available

### Candidate construction
- start from DSC sign and ruler route
- add Venus for affection/value pattern
- add Mars for conflict/desire/boundary route
- add Moon for need/attachment route
- add house weighting from `5H / 7H / 8H`
- select strongest subtype

### Subtype routing
- `trust_steadiness`
- `attraction_warmth`
- `boundary_conflict`
- `intimacy_depth`
- `emotional_need_affection`

### Confidence scoring

Suggested scoring components:
- `dsc_route_strength`: `0.0 - 0.25`
- `dsc_ruler_strength`: `0.0 - 0.20`
- `venus_support`: `0.0 - 0.15`
- `mars_support`: `0.0 - 0.15`
- `moon_support`: `0.0 - 0.10`
- `house_scene_support`: `0.0 - 0.10`
- `contradiction_coherence`: `0.0 - 0.05`

Reduce score when:
- Venus/Mars/Moon point to unrelated subtypes
- only attraction exists but trust/depth route is absent

### `domain_reason`

Examples:
- `DSC route`
- `DSC ruler involved`
- `Venus relationship signature`
- `Mars boundary/desire signature`
- `Moon attachment signature`
- `5H/7H/8H reinforcement`

### `public_job`

Allowed values in first rollout:
- `main_relationship`
- `support_gift`
- `detail_shadow`
- `debug_only`

### Exact registry override

Registry wins only when:
- exact packet matches relationship subtype
- chart facts match
- domain and `public_job` match

### Generic fallback suppression

Composed relationship can beat raw generic relationship fallback only when:
- subtype is explicit
- confidence >= medium
- `lived_scene` exists
- evidence trace includes DSC + ruler + at least one of Venus/Mars/Moon

### Public eligibility

Default `v0.9`:
- debug: yes
- detail: yes if confidence >= medium
- support: yes if confidence >= medium and subtype explicit
- public_main: no by default

## 6.3 `career_route`

### Inputs
- `MC`
- MC ruler
- `10H` planets
- Sun / Mars / Saturn / Venus / Jupiter links
- public angularity
- career-related chart spine if available

### Candidate construction
- start from MC sign and ruler route
- add `10H` planets with role-specific meaning
- use public angularity as emphasis, not as meaning owner
- select one dominant subtype

### Subtype routing
- `public_voice`
- `authority_responsibility`
- `creative_visibility`
- `action_initiative`
- `strategic_role`
- `invisible_preparation_before_visibility`

### Confidence scoring

Suggested scoring components:
- `mc_route_strength`: `0.0 - 0.25`
- `mc_ruler_strength`: `0.0 - 0.25`
- `tenth_house_support`: `0.0 - 0.20`
- `public_planet_support`: `0.0 - 0.15`
- `angularity_bonus`: `0.0 - 0.10`
- `subtype_coherence`: `0.0 - 0.05`

Reduce score when:
- MC exists without scene support
- route is only generic visibility wording

### `domain_reason`

Examples:
- `MC route`
- `MC ruler involved`
- `10H planet`
- `public angularity`
- `career spine route`

### `public_job`

Allowed values in first rollout:
- `main_career`
- `public_support`
- `detail_shadow`
- `debug_only`

### Exact registry override

Registry wins only when:
- chart facts match
- packet covers same public-role context
- `public_job` matches

### Generic fallback suppression

Composed career can beat raw generic career fallback only when:
- confidence >= medium
- subtype explicit
- lived scene exists
- MC + ruler + scene evidence are all present

### Public eligibility

Default `v0.9`:
- debug: yes
- detail: yes if confidence >= medium
- support: yes if confidence >= medium and subtype explicit
- public_main: no by default

## 6.4 `moon_signature`

### Inputs
- Moon sign
- Moon house
- Moon aspects
- Moon ruler route
- `IC / 4H` links
- relational links if Moon routes to `7H / 8H`
- body/routine links if Moon routes to `6H`

### Candidate construction
- start from Moon sign tone
- add Moon house scene
- route through Moon ruler
- use aspect pattern to choose subtype emphasis
- add `IC / 4H`, `7H / 8H`, or `6H` reinforcement when present

### Subtype routing
- `emotional_rhythm`
- `home_inner_security`
- `relational_need`
- `daily_sensitivity`
- `creative_emotional_expression`
- `private_emotional_processing`

### Confidence scoring

Suggested scoring components:
- `moon_sign_strength`: `0.0 - 0.15`
- `moon_house_scene`: `0.0 - 0.20`
- `moon_ruler_route`: `0.0 - 0.20`
- `aspect_support`: `0.0 - 0.20`
- `reinforcement_support`: `0.0 - 0.15`
- `subtype_coherence`: `0.0 - 0.10`

Reduce score when:
- only sign meaning exists
- Moon aspects are noisy without clear subtype

### `domain_reason`

Examples:
- `Moon need signature`
- `Moon house scene`
- `Moon ruler route`
- `IC/4H reinforcement`
- `Moon relational route`
- `Moon daily-rhythm route`

### `public_job`

Allowed values in first rollout:
- `public_support`
- `support_gift`
- `detail_shadow`
- `debug_only`

### Exact registry override

Registry wins only when:
- exact Moon-related packet is chart-fact safe
- domain context matches
- `public_job` matches

### Generic fallback suppression

Composed Moon candidate can beat raw generic emotional fallback only when:
- subtype explicit
- confidence >= medium
- lived scene exists
- Moon route has clear scene evidence

### Public eligibility

Default `v0.9`:
- debug: yes
- detail: yes if confidence >= medium
- support: yes if confidence >= medium and subtype explicit
- public_main: no by default

## 7. `domain_reason` and `public_job`

These fields are mandatory for composed candidates.

## 7.1 `domain_reason`

Purpose:
- justify why a candidate belongs to a domain
- keep the same anchor from drifting into wrong cluster ownership
- make audit reasoning visible

Type:

```python
domain_reason: list[str]
```

Allowed examples:
- `ASC route`
- `chart ruler route`
- `DSC ruler involved`
- `Venus relationship signature`
- `MC ruler involved`
- `10H planet`
- `Moon need signature`

## 7.2 `public_job`

Purpose:
- separate semantic meaning from surface role
- allow ClusterPlan to gate composed candidates conservatively

Type:

```python
public_job: str
```

Allowed initial set:
- `main_identity`
- `main_relationship`
- `main_career`
- `public_support`
- `support_gift`
- `detail_shadow`
- `debug_only`

`hero` is intentionally excluded from first rollout.

## 8. `source_type = composed_semantic`

Every composed candidate must expose:

```python
source_type = "composed_semantic"
```

This must flow through:
- candidate packet dicts in `natal_promise_packets.py`
- `ClusterPacketMemberV1.source_type`
- cluster-level source type rollups in `natal_promise_cluster_plan.py`
- audit metrics in ClusterPlan output

No public schema expansion is required beyond internal trace propagation already used for `source_type`.

## 9. Public Eligibility Gates

Composed candidates must not automatically become `public_main`.

Required gates:
- chart-fact safe
- domain-clear
- `domain_reason` present
- `public_job` present
- `lived_scene` present
- `evidence_trace` present
- confidence threshold satisfied
- not duplicative with stronger exact registry packet
- not generic/template-only

Suggested first-rollout policy:

```text
debug:
  always allowed when candidate is valid

detail:
  allowed when confidence >= medium

public_support:
  allowed when confidence >= medium
  and lived_scene exists
  and domain_reason exists

public_main:
  disabled by default
  only future feature-flag rollout
```

Important guardrail:
- even high-confidence composed candidates cannot enter `public_main` until `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=true`
- confidence alone is not enough for `public_main` in `v0.9a`

## 10. Exact Registry Override Rules

Exact registry should override composed semantics only when:
- chart facts match
- domain matches
- `public_job` matches
- the exact packet is more specific
- cluster context supports the same meaning

Composed candidate should remain preferred when:
- exact registry packet is domain-misaligned
- exact registry packet would force wrong surface role
- exact packet is semantically narrower than the route needed

## 11. How Composed Candidates Beat Raw Generic Fallback

Composed candidate may beat `raw_generic_fallback` only when all are true:
- chart-fact safe
- traceable
- domain-clear
- `lived_scene` backed
- sufficiently confident
- not duplicative with stronger exact packet

Important:
- this does not mean composed candidates beat all fallback immediately
- they should first beat only `raw_generic_fallback`
- `cluster_specific_fallback` and `customized_fallback_with_bespoke_copy` are lower-risk and can remain ahead until later rollout

## 12. Integration Points

## 12.1 `backend/app/natal/natal_promise_packets.py`

This is the primary insertion point for composed candidate construction.

Implementation role in later phase:
- add a new internal builder stage after `v0.6` discovery scaffolds
- emit composed candidates in `candidate_inventory` mode
- optionally emit eligible composed candidates in `selected` mode only after later rollout flag

Suggested additions:
- `ComposedSemanticCandidateV1` normalizer to existing packet dict shape
- `_build_v0_9_composed_semantic_candidates(...)`
- `_build_identity_route_candidates(...)`
- `_build_relationship_route_candidates(...)`
- `_build_career_route_candidates(...)`
- `_build_moon_signature_candidates(...)`
- `_composed_candidate_to_packet(...)`

Suggested build order inside `build_natal_promise_packets_v1(...)`:

```text
existing section/thread candidates
-> existing chart-signature candidates
-> existing v0.6 discovery candidates
-> new v0.9 composed semantic candidates
-> source type annotation
```

Important:
- no registry entries are created here
- no renderer copy is generated here

## 12.2 `backend/app/natal/natal_promise_cluster_plan.py`

This is the gating and ranking point.

Implementation role in later phase:
- recognize `source_type = composed_semantic`
- keep composed candidates out of `public_main` by default
- allow debug/detail/support participation
- apply exact-registry override rules
- apply raw-generic-fallback suppression rules

Suggested additions:
- composed candidate eligibility evaluator
- exact-vs-composed context compatibility helper
- raw-generic-fallback suppression helper
- audit metrics for composed candidate counts by route family

Potential helper names:
- `_composed_candidate_public_eligibility(...)`
- `_exact_registry_context_compatible(...)`
- `_composed_beats_raw_generic_fallback(...)`
- `_composed_family_distribution(...)`

## 12.3 `backend/app/natal/public_builder.py`

This file should not change public output behavior in the first phase.

Implementation role in later phase:
- pass composed candidates through packet and cluster plan traces
- expose them only through existing internal debug structures
- do not let renderer infer meaning from them directly

Safe first-rollout use:
- include composed candidates in `candidate_inventory`
- include them in ClusterPlan debug metadata
- keep public surfaces unchanged unless later feature flag explicitly allows support/detail participation

Phase-1 no-op rule:
- with `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`
- and `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`
- projection public surfaces must remain unchanged

Accepted golden outputs should remain:
- byte-stable where current tests expect byte stability
- semantically equivalent where snapshot policy allows semantic equivalence instead of byte identity

## 13. Feature Flag Proposal

Use staged flags instead of one large release switch.

Suggested flags:

### `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9`
- master on/off for composed candidate generation
- initial intended use: debug only

### `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT`
- allows composed candidates to participate in `detail` and `public_support`

### `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN`
- later-only flag
- allows composed candidates to be considered for `public_main`
- should remain off in first rollout

Safer default:

```text
ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=false
ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false
ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false
```

Then later:
- enable master flag in tests and targeted review runs first
- turn on detail/support first
- public_main last

## 14. Tests to Add

## 14.1 Candidate generation tests
- composed candidates are generated for eligible `identity_route`
- composed candidates are generated for eligible `career_route`
- `source_type == composed_semantic`

## 14.2 Eligibility tests
- composed candidates are not `public_main` by default
- composed candidates may appear in debug only with base flag
- composed candidates may appear in detail/support only with dedicated flag
- composed candidates without `lived_scene` remain non-public
- composed candidates without `domain_reason` remain non-public

## 14.3 Override tests
- exact registry beats composed only when context-compatible
- composed candidate does not suppress stronger exact packet
- composed candidate can beat `raw_generic_fallback` when eligible
- composed candidate does not automatically beat `cluster_specific_fallback`

## 14.4 Safety tests
- no chart-fact mismatches
- no duplicate `public_main` with stronger exact packet
- no renderer dependency in meaning selection

## 14.5 Regression tests

Accepted goldens that must stay stable:
- Istanbul 1996
- Adana 1998
- Istanbul 2020
- Izmir 1996
- Istanbul 1994
- Istanbul 1997

## 14.6 Public-output no-op tests

- with master flag on but detail/support/public_main flags off, public projection surfaces remain unchanged
- accepted goldens remain byte-stable where current tests assert byte stability
- where snapshot policy is semantic rather than byte-level, outputs remain semantically equivalent

## 14.7 Debug metrics tests

- `composed_candidate_count` is present
- `composed_candidate_family_distribution` is present
- `composed_candidate_confidence_distribution` is present
- `composed_candidate_public_eligibility_distribution` is present
- `composed_vs_generic_fallback_opportunities` is present
- all metrics remain debug-only and do not alter selected public surfaces

## 15. Rollout Sequence

Recommended rollout:

### Phase 1: debug-only
- generate composed candidates
- include in `candidate_inventory`
- include in ClusterPlan debug metrics
- no public effect
- no public-surface differences when support/main flags remain off

### Phase 2: detail/support eligible
- allow composed candidates into `detail`
- allow composed candidates into `public_support`
- still no `public_main`

### Phase 3: public_main eligible later
- only after audit validation
- only with stricter confidence thresholds
- only under feature flag

## 16. Recommended Slice Split

Recommended safer split:

### `v0.9a`
- `identity_route`
- `career_route`

Why first:
- they are less relationally ambiguous
- they map directly to repeated public-main fallback owners
- they are less likely to create surface duplication with current exact packets
- they are safer for a debug-only no-op rollout

### `v0.9b`
- `relationship_route`
- `moon_signature`

Why second:
- both are more subtype-sensitive
- both have more domain overlap
- both are more likely to create context conflicts with existing exact packets

Hard scope rule:
- do not implement `relationship_route` or `moon_signature` in `v0.9a`
- they require separate review before activation

Alternative split is not recommended unless code findings later show relationship and Moon are simpler than expected.

## 17. Regression Requirements for Accepted Goldens

Before any later implementation phase is accepted:
- accepted golden public surfaces must remain stable by default
- no P0 truthfulness regressions
- no new false anchors
- no increase in duplicate surface ownership
- no renderer-dependent meaning behavior

Specific rule:
- if `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`, accepted goldens should not materially change public output

## 18. 50-Chart Mixed Batch Success Metrics

The first future implementation should be judged on mixed-chart diagnostics, not copy beauty.

Primary success metrics:
- `composed_semantic` candidate count > `0`
- no chart-fact mismatch increase
- lower `raw_generic_fallback` ownership in representative mixed charts
- reduced `generic_fallback_public_main` warnings
- support/detail less empty where composed candidates exist
- accepted goldens stable

Required debug metrics:
- `composed_candidate_count`
- `composed_candidate_family_distribution`
- `composed_candidate_confidence_distribution`
- `composed_candidate_public_eligibility_distribution`
- `composed_vs_generic_fallback_opportunities`

Representative low-health charts to recheck:
- `fix06_grand_trine_flow`
- `ankara_1993_06_10`
- `buenos_aires_1980_09_09`
- `dubai_1995_01_03`

Target direction:
- do not maximize candidate count
- reduce raw generic fallback ownership with traceable composed candidates

## 19. Final Implementation Rule

Renderer must not choose meaning.

ClusterPlan remains the public-surface selector.

`v0.9` should add a semantic layer, not a second renderer and not a silent public-behavior rewrite.

The correct rollout sequence is:

```text
discovery
-> composed_semantic candidate generation
-> exact registry compatibility check
-> ClusterPlan gating
-> renderer consumption only after selection
```

That preserves the current SHOU architecture while making it capable of scaling beyond registry-only expansion.
