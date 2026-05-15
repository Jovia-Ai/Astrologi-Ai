# v0.9a.1 Public Voice Detail-Only Post-Rollout Review

## Scope

This review covers the `v0.9a.1` rollout slice requested for:

- `career_route` only
- subtype `public_voice` only
- `detail` eligibility only

Explicitly out of scope and still disabled:

- `public_support`
- `public_main`
- non-`public_voice` career subtypes
- `identity_route` rollout
- `relationship_route`
- `moon_signature`
- renderer changes
- registry additions

## Flag State

Validated with:

- `ENABLE_NATAL_PROMISE_PROJECTION_V1=true`
- `ENABLE_NATAL_PROMISE_PACKET_DEBUG=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

Default runtime remains safe:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=false`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=false`

So the rollout is opt-in and inert by default.

## Implementation Behavior

`public_voice` composed career candidates now become `detail_eligible=true` only when all requested gates hold:

- subtype is `public_voice`
- `confidence_tier == high`
- `confidence >= 0.88`
- `chart_facts_match == true`
- `domain_reason` includes `MC route`, `MC ruler involved`, `10H planet`
- `evidence_trace.family_inputs` includes `MC`, `MC_ruler`, `10H_planets`
- subtype evidence includes a Mercury public anchor
- at least `2` distinct visible/public anchors are present
- `lived_scene` names public role / speech / positioning
- current owner quality is `raw_generic_fallback`

When that gate passes:

- composed packet stays suppressed from `public_main`
- composed packet stays suppressed from `public_support`
- composed packet is retained for `detail` and `debug`

This is represented through suppression state:

- `keep_for = ["detail", "debug"]`

Important current behavior:

- rollout is expressed through composed-packet eligibility and suppression routing
- `public_main` cluster selection remains unchanged
- `public_support` remains unchanged
- `detail_cluster_ids` do not need to grow for this rollout to work
- the slice is intentionally packet-level and not a cluster-selection rewrite

## Affected Charts

Validated target charts:

- `fix04_h10_career_stellium`
- `tokyo_1998_06_21`
- `toronto_1976_06_26`

For these charts, tests assert:

- `composed_career_route_v0_9a` exists in candidate inventory
- `subtype == public_voice`
- `source_type == composed_semantic`
- `public_eligibility.detail_eligible == true`
- `public_eligibility.public_support_eligible == false`
- `public_eligibility.public_main_eligible == false`
- suppression state keeps the packet in `detail` and `debug`
- composed packet does not enter `public_main`
- composed packet does not enter `public_support`

Representative composed packet shape on target charts:

- `family: career_route`
- `subtype: public_voice`
- `confidence: 0.94`
- `confidence_tier: high`
- `domain_reason: ["MC route", "MC ruler involved", "10H planet"]`
- `public_job: debug_only`

## Non-Target Charts Kept Debug-Only

Validated debug-only holdouts:

- `kutahya_1959_10_21`
- `izmir_2007_07_19`
- `izmir_1996_05_20`
- `mexico_city_1988_08_31`
- `dubai_1995_01_03`

For these charts, tests assert:

- `composed_career_route_v0_9a` remains suppressed with `keep_for = ["debug"]`
- no accidental `detail` promotion occurs
- non-`public_voice` subtypes remain outside rollout scope

## Before / After Public Surfaces

### Intended delta

The rollout is allowed to expose `public_voice` composed packets only at the `detail` layer.

It must not change:

- `public_main`
- `public_support`
- renderer wording logic
- exact-registry ownership

### Confirmed public constraints

Post-rollout validations confirm:

- `public_main` stayed off for composed semantics
- `public_support` stayed off for composed semantics
- no composed packet became `public_main` even at high confidence
- exact/chart-specific owners were not overridden

### Detail surface note

This rollout currently works through suppression and packet eligibility rather than a new public-main or support cluster. In other words:

- the packet becomes `detail`-eligible
- the cluster plan records that eligibility
- the packet remains blocked from `public_support` and `public_main`

## Detail Clusters Added

No new `public_main` clusters were added.

No `public_support` clusters were added.

For this rollout, the meaningful delta is:

- composed packet eligibility flips from debug-only to detail-eligible
- suppression state flips from `["debug"]` to `["detail", "debug"]`

So the rollout should be understood as a packet-level detail admission, not a new-cluster rollout.

## Public Main Stayed Off

Explicitly validated:

- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`
- `public_eligibility.public_main_eligible == false`
- composed packet ids do not appear in `surface_plan.public_main_cluster_ids`

## Accepted Golden No-Op Confirmation

Golden regression coverage passed with rollout flags enabled and `public_main` still disabled for:

- Istanbul 1996
- Adana 1998
- Istanbul 2020
- Izmir 1996
- Istanbul 1994
- Istanbul 1997

The regression assertion is projection-surface no-op:

- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

remained stable under the rollout flag set for accepted goldens.

## Exact / Chart-Specific Owner Protection

Protection remains intact:

- exact/chart-specific public career owners are not displaced by composed `public_voice`
- the rollout only opens a detail lane
- registry-backed public ownership remains stronger than composed packets in this slice

## Test Results

Focused rollout-facing suite:

- `backend/tests/test_natal_public_builder.py`: `22 passed`

Broader regression suite:

- `backend/tests/test_natal_promise_packets.py`: included in regression run
- `backend/tests/test_natal_promise_cluster_plan.py`: included in regression run
- `backend/tests/test_projection_shadow_v1_builder.py`: included in regression run
- combined result: `74 passed`

Total validated in this pass:

- `96 passed`

## Final Assessment

`v0.9a.1` is now implemented as a tightly scoped, flag-gated rollout:

- only `career_route.public_voice`
- only `detail` eligibility
- no renderer changes
- no registry changes
- no `public_support`
- no `public_main`
- accepted goldens stable

This keeps the rollout narrow enough for further qualitative review before any future support-level expansion.
