# v0.9a Scoring and Opportunity Calibration Report

Date: 2026-05-14

Scope:
- `identity_route`
- `career_route`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

Guardrails kept:
- no `detail/support` rollout
- no `public_main` rollout
- no renderer changes
- no registry changes
- no public-output changes
- no `relationship_route`
- no `moon_signature`

## Executive Summary

The calibration pass improved precision without changing public behavior.

Main outcome:
- `career_route` became meaningfully narrower and more useful.
- `identity_route` opportunity over-counts were eliminated from replacement metrics.
- `opportunity` reporting now separates:
  - `high_priority_opportunity`
  - `medium_priority_opportunity`
  - `debug_observation_only`

Current readiness verdict:
- `public_main`: still not eligible
- `detail/support`: still not ready for rollout
- `career_route`: strongest calibrated debug signal
- `identity_route`: now more trustworthy as an audit/debug layer because it no longer over-claims replacement value against already-acceptable identity owners

## Aggregate Before / After

`Before` values below are the accepted pre-calibration `v0.9a` debug batch baseline.

| Metric | Before | After |
| --- | ---: | ---: |
| `composed_identity_route_count` | 44 | 44 |
| `composed_career_route_count` | 40 | 29 |
| total composed candidates | 84 | 73 |
| `high` confidence | 29 | 35 |
| `medium` confidence | 37 | 31 |
| `low` confidence | 18 | 7 |
| total opportunities | 52 | 23 |
| `career_route` opportunities | 34 | 23 |
| `identity_route` opportunities | 18 | 0 |
| `debug_observation_only` | not separated | 24 |

Interpretation:
- The calibration removed weak or overly broad career candidates instead of letting them inflate opportunity counts.
- The confidence mix improved materially: fewer total candidates, more `high`, and much fewer `low`.
- Identity replacement pressure was intentionally reduced to zero. Identity now contributes audit value without pushing against already-acceptable exact/chart-specific owners.

## Career Route Calibration

Implemented calibration rules:
- `strategic_role` is down-ranked when there is no subtype-defining public planet support.
- `invisible_preparation_before_visibility` now requires both:
  - a `12H/backstage/ruler-hidden` signature
  - a visible career anchor beyond private planets alone
- subtype-specific evidence bonuses now reward:
  - `Mercury -> public_voice`
  - `Saturn -> authority_responsibility`
  - `Venus/Neptune -> creative_visibility`
  - `Mars -> action_initiative`
  - `12H/ruler-hidden -> invisible_preparation_before_visibility`

### Career Subtype Distribution

| Subtype | Before | After |
| --- | ---: | ---: |
| `strategic_role` | 10 | 0 |
| `invisible_preparation_before_visibility` | 12 | 11 |
| `public_voice` | 5 | 7 |
| `authority_responsibility` | 4 | 2 |
| `creative_visibility` | 5 | 5 |
| `action_initiative` | 4 | 4 |

### Career Opportunity Distribution

Before:
- `strategic_role`: 9 opportunities
- `invisible_preparation_before_visibility`: 10 opportunities
- `public_voice`: 4 opportunities
- `authority_responsibility`: 3 opportunities
- `creative_visibility`: 5 opportunities
- `action_initiative`: 3 opportunities

After:
- `public_voice`: 5 `high_priority`
- `invisible_preparation_before_visibility`: 9 `high_priority`
- `creative_visibility`: 4 `high_priority`, 1 `medium_priority`
- `action_initiative`: 2 `high_priority`, 1 `medium_priority`
- `authority_responsibility`: 1 `high_priority`
- `strategic_role`: 0 candidates, 0 opportunities

### Low-Confidence Career Opportunities

Before:
- `strategic_role`: 8 low-confidence opportunities
- `invisible_preparation_before_visibility`: 3 low-confidence opportunities

After:
- no low-confidence opportunities remain in the surfaced opportunity set

### Career Calibration Read

This is the strongest win in the pass.

The system now does a better job of:
- rewarding subtype-defining evidence instead of generic MC/ruler presence alone
- preventing `strategic_role` from masquerading as a public-replacement opportunity
- keeping backstage/invisible-preparation logic tied to actual visibility anchors

Remaining caution:
- `invisible_preparation_before_visibility` still produces many high-priority cases
- some medium-confidence cases like `dubai_1995_01_03` are useful, but should remain debug-only until later detail/support thresholds are reviewed

## Identity Route Opportunity Calibration

Implemented calibration rules:
- identity opportunity is no longer counted only because the current owner `source_type` is `generic_fallback`
- opportunity is down-ranked or excluded when the current owner is already:
  - semantically acceptable
  - chart-specific
  - cluster-specific fallback with a good lived scene
  - customized fallback with bespoke copy
  - exact registry

### Identity Opportunity Change

| Metric | Before | After |
| --- | ---: | ---: |
| `identity_route` composed candidates | 44 | 44 |
| `identity_route` opportunities | 18 | 0 |
| `identity_route` debug observations | not separated | 20 |

This is the intended behavior.

Identity remains present as semantic audit material, but it no longer falsely claims replacement urgency against already-usable identity owners.

### Representative Identity Over-Count Fixes

These charts previously looked like replacement opportunities but now resolve as `debug_observation_only`:
- `adana_1998_09_12`
  - current owner: `mars_square_chiron_tender_courage`
  - owner quality: `customized_fallback_with_bespoke_copy`
- `istanbul_2020_04_10`
  - current owner: `gemini_asc_venus_1h_social_relational_presence_chart_exact`
  - owner quality: `cluster_specific_fallback`
- `istanbul_1994_06_25`
  - current owner: `leo_asc_sun_cancer_11h_warm_visibility_belonging_chart_exact`
  - owner quality: `exact_registry`
- `kutahya_1959_10_21`
  - current owner: `saturn_trine_pluto_deep_resilience_chart_exact`
  - owner quality: `cluster_specific_fallback`
- `new_york_1984_10_02`
  - current owner remains acceptable enough to stay in debug-observation territory

## Opportunity Severity Taxonomy

Current counts:

| Severity | Count |
| --- | ---: |
| `high_priority_opportunity` | 21 |
| `medium_priority_opportunity` | 2 |
| `debug_observation_only` | 24 |

Interpretation:
- high-priority cases are now tightly career-dominant and tied to `raw_generic_fallback`
- medium-priority cases identify usable but non-urgent chart-specific/customized owners
- debug-only observations now carry most identity-route audit value

## Top High-Priority Opportunities

These are the clearest current `composed_semantic -> raw_generic_fallback` replacement opportunities in debug metrics:

1. `fix04_h10_career_stellium`
   - subtype: `public_voice`
   - confidence: `high`
   - current owner quality: `raw_generic_fallback`
2. `kutahya_1959_10_21`
   - subtype: `creative_visibility`
   - confidence: `high`
   - current owner quality: `raw_generic_fallback`
3. `izmir_2007_07_19`
   - subtype: `authority_responsibility`
   - confidence: `high`
   - current owner quality: `raw_generic_fallback`
4. `izmir_1996_05_20`
   - subtype: `public_voice`
   - confidence: `high`
   - current owner quality: `raw_generic_fallback`
5. `mexico_city_1988_08_31`
   - subtype: `creative_visibility`
   - confidence: `high`
   - current owner quality: `raw_generic_fallback`
6. `dubai_1995_01_03`
   - subtype: `invisible_preparation_before_visibility`
   - confidence: `medium`
   - current owner quality: `raw_generic_fallback`

Other strong high-priority career cases:
- `bursa_1987_11_03`
- `konya_1974_05_19`
- `trabzon_2001_09_14`
- `diyarbakir_1994_03_22`
- `tokyo_1998_06_21`
- `madrid_2004_04_18`
- `mumbai_1977_07_07`
- `toronto_1976_06_26`

## Top Medium-Priority Opportunities

These are useful but not urgent:

1. `istanbul_2020_04_10`
   - subtype: `action_initiative`
   - confidence: `high`
   - current owner quality: `customized_fallback_with_bespoke_copy`
   - current owner: `aquarius_mc_mars_conjunct_mc_visible_freedom_drive`
2. `samsun_1970_07_29`
   - subtype: `creative_visibility`
   - confidence: `medium`
   - current owner quality: `customized_fallback_with_bespoke_copy`

These cases should remain debug-only for now.

## Debug-Only Observations

Debug observations now hold the non-urgent semantic inventory:

- `identity_route`: 20
- `career_route`: 4

Representative debug-only observations:
- `adana_1998_09_12`
  - identity owner already semantically acceptable
- `istanbul_1994_06_25`
  - both identity and career owners are exact-registry quality
- `istanbul_1997_01_21`
  - career owner is exact-registry quality
- `fix01_leo_leo_classic`
  - identity candidate is interesting but the current identity owner is already cluster-specific enough

## Accepted Golden Over-Count Reduction

The key reduction goal was met:
- accepted/good identity owners are no longer counted as replacement opportunities
- they now appear as `debug_observation_only` when composed identity still adds audit value

Examples:
- `adana_1998_09_12`: demoted from opportunity logic to debug observation
- `istanbul_1994_06_25`: exact-registry identity/career owners stay protected
- `istanbul_1997_01_21`: exact-registry career owner stays protected
- `istanbul_2020_04_10`: identity now debug-only; only career remains as a non-urgent medium-priority case

## Public Output and Safety

Confirmed:
- composed candidates remain debug-only
- `detail/support/public_main` remain disabled
- no public surfaces changed
- no chart-fact safety issues were introduced
- no composed candidate reported `chart_facts_match=false`

Chart-fact safety:
- `mismatch_candidates`: `0`

## Validation

Focused suite:

```text
backend/tests/test_natal_promise_packets.py: 13 passed
backend/tests/test_natal_promise_cluster_plan.py: 18 passed
backend/tests/test_natal_public_builder.py + backend/tests/test_projection_shadow_v1_builder.py: 61 passed
total: 92 passed
```

Relevant regression coverage now includes:
- accepted goldens stable
- composed candidates remain debug-only
- no public output changes with public flags off
- raw generic career owner -> `high_priority_opportunity`
- chart-specific acceptable identity owner -> `debug_observation_only`

## Calibration Verdict

`v0.9a` calibration improved debug metrics materially, but it does **not** justify `detail/support` rollout yet.

Ready now:
- better `career_route` subtype precision
- much cleaner opportunity severity reporting
- identity over-count suppression

Not ready yet:
- enabling composed semantics on any public surface
- treating medium-confidence career candidates as support by default
- broadening beyond `identity_route` and `career_route`

Current recommendation:
- keep `v0.9a` in debug-only mode
- use this calibrated signal as the baseline for any future detail/support threshold review
