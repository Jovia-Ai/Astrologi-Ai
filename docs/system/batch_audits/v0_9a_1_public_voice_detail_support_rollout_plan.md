# v0.9a.1 Public Voice Detail/Support Rollout Plan

Date: 2026-05-14

Status:
- planning only
- no code changes
- no flag changes
- no renderer changes
- no registry changes
- no public output changes

Scope:
- `career_route`
- subtype: `public_voice`

Out of scope:
- `creative_visibility`
- `authority_responsibility`
- `action_initiative`
- `invisible_preparation_before_visibility`
- `identity_route`
- `relationship_route`
- `moon_signature`
- any `public_main` eligibility

Source note:
- The requested source file `docs/system/batch_audits/v0_9a_high_priority_career_candidate_quality_review.md` is not present in the workspace.
- This plan is therefore grounded in the accepted current review artifacts:
  - `docs/system/batch_audits/v0_9a_scoring_opportunity_calibration_report.md`
  - `docs/system/batch_audits/v0_9a_identity_career_debug_candidate_review.md`
  - the accepted qualitative review of high-priority career opportunities for the reviewed charts

## Decision Summary

`public_voice` is the only `career_route` subtype that currently looks safe enough to consider for a later controlled `detail/public_support` rollout.

Why this subtype first:
- it has the cleanest evidence model
- it is the least semantically fuzzy of the current career subtypes
- it repeatedly appears in high-priority charts where current career ownership is still `raw_generic_fallback`
- its lived scene is concrete and naturally maps to SHOU public language without forcing registry work first

This plan does **not** recommend enabling rollout yet.

It defines:
- exact future thresholds for `detail`
- exact future thresholds for `public_support`
- which reviewed charts qualify if implementation happens later
- which charts must remain debug-only
- the guardrails needed to keep accepted goldens stable

## Core Policy

`public_voice` can only be considered for future public eligibility when all of the following remain true:
- `public_main` stays disabled
- exact registry and chart-specific accepted owners still win where context is already good
- `detail/support` remains flag-gated
- when the flag is off, public output is a byte-level or snapshot-equivalent no-op

Rule:

`public_voice` may become:
- `detail` eligible first
- then `public_support` eligible later

It must **not** become `public_main` eligible in `v0.9a.1`.

## Proposed Feature Flags

Keep current flags:
- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN`

Add one subtype gate for future implementation:
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT`

Required behavior:
- default `false`
- no effect unless `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- no effect on `public_main`
- no effect on non-`public_voice` subtypes

Hard no-main rule:
- even if `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=true`
- and even if `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=true`
- `public_voice` still cannot enter `public_main` unless `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=true`
- for `v0.9a.1`, that `public_main` path remains unsupported by policy

## Exact Eligibility Threshold for Detail

`public_voice` should become `detail` eligible only when all conditions pass:

1. subtype is exactly `public_voice`
2. `confidence_tier == high`
3. numeric `confidence >= 0.88`
4. `chart_facts_match == true`
5. `public_job == debug_only` at generation time, then re-labeled by ClusterPlan only if rollout flag allows detail
6. `domain_reason` contains all:
   - `MC route`
   - `MC ruler involved`
   - `10H planet`
7. `evidence_trace.family_inputs` contains:
   - `MC`
   - `MC_ruler`
   - `10H_planets`
8. subtype-defining evidence includes at least one of:
   - `Mercury` as `MC` ruler in `10H` or `11H`
   - `Mercury` physically in `10H`
9. visible career anchor count:
   - at least `2` distinct visible anchors
   - recommended accepted combinations:
     - `MC Gemini + Mercury 10H`
     - `MC Gemini + Mercury ruler 10H + Sun 10H`
     - `MC Gemini + Mercury 10H + multiple 10H planets`
10. lived scene quality:
   - `lived_scene` must be explicit public-role language
   - must mention some version of speech / positioning / outward role, not only “visibility”
11. current owner quality:
   - should be `raw_generic_fallback`
   - if current owner is `customized_fallback_with_bespoke_copy`, keep as debug-only or later `public_support` candidate, not `detail` by default

Interpretation:
- `detail` is appropriate when the composed candidate is clearly stronger than the current raw generic owner, but the system is not yet ready to promote it into a support card that could influence overall narrative emphasis

## Exact Eligibility Threshold for Public Support

`public_voice` should become `public_support` eligible only when all `detail` conditions pass, plus:

1. numeric `confidence >= 0.92`
2. `confidence_tier == high`
3. there are at least `3` visible public anchors, with at least one being Mercury-specific
4. the chart’s current public-main career owner is still `raw_generic_fallback`
5. the current public-main career copy is generic/template-level, not merely technically generic
6. the composed candidate’s lived scene is distinct enough that it would not duplicate the current main card
7. no accepted golden chart would be affected by the new gating
8. no exact registry packet in the same domain already expresses the same public-voice meaning adequately

Interpretation:
- `public_support` should only be used when `public_voice` is not just valid but clearly useful as a second surface on top of a still-generic career owner

## Which Reviewed Charts Qualify

### Qualify for Future Detail

These reviewed charts meet the recommended `detail` threshold:
- `fix04_h10_career_stellium`
  - subtype: `public_voice`
  - confidence: `0.94`
  - evidence: `MC Gemini + Mercury 10H + Mars 10H`
- `tokyo_1998_06_21`
  - subtype: `public_voice`
  - confidence: `0.94`
  - evidence: `MC Gemini + Mercury 10H + Sun 10H`
- `toronto_1976_06_26`
  - subtype: `public_voice`
  - confidence: `0.94`
  - evidence: `MC Gemini + Mercury 10H + Sun/Moon/Venus 10H`

### Qualify for Future Public Support

These reviewed charts also qualify for later `public_support`, if and only if the future rollout proves no-op safety elsewhere:
- `fix04_h10_career_stellium`
- `tokyo_1998_06_21`
- `toronto_1976_06_26`

Reason:
- all three are high-confidence `public_voice`
- all three currently point at `raw_generic_fallback`
- all three have stronger domain specificity than the current public career owner
- all three have enough visible public-role evidence to justify a support-layer appearance later

## Which Reviewed Charts Must Remain Debug-Only

Remain debug-only in `v0.9a.1` by scope:
- `kutahya_1959_10_21`
  - subtype: `creative_visibility`
- `izmir_2007_07_19`
  - subtype: `authority_responsibility`
- `izmir_1996_05_20`
  - subtype: `invisible_preparation_before_visibility`
- `mexico_city_1988_08_31`
  - subtype: `creative_visibility`
- `dubai_1995_01_03`
  - subtype: `invisible_preparation_before_visibility`

Also remain debug-only because they are out of scope:
- any `career_route` subtype other than `public_voice`
- any `identity_route` candidate

## No Public Main Rule

For `v0.9a.1`, `public_main` stays disabled by policy.

Implementation rule for later:
- `public_eligibility.public_main_eligible` must stay `false`
- ClusterPlan must ignore `public_voice` for `public_main` even if:
  - subtype is `public_voice`
  - confidence is `high`
  - support/detail flag is enabled

This is a hard rollout guardrail, not a scoring preference.

## Public No-Op Expectations When Flag Off

When:
- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=false`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

Expected:
- public surfaces remain unchanged
- `profile_narrative_projection_v1` unchanged
- `profile_v8_projection_v1` unchanged
- composed candidates remain debug-only
- traceability and audit metrics may show `public_voice` candidates, but surface selection does not change

## Accepted Golden Safety

Accepted goldens that must remain unchanged:
- `Istanbul 1996`
- `Adana 1998`
- `Istanbul 2020`
- `Izmir 1996`
- `Istanbul 1994`
- `Istanbul 1997`

Guarantee strategy:
- do not allow `public_main`
- only allow `detail/support` behind subtype-specific flag
- require exact-registry and chart-specific owner compatibility checks before any promotion
- if current career owner is already:
  - `exact_registry`
  - `cluster_specific_fallback`
  - `customized_fallback_with_bespoke_copy`
  then `public_voice` must stay debug-only

Immediate implication for reviewed goldens:
- `Istanbul 1997` must remain debug-only because career ownership is already exact and semantically correct
- `Istanbul 1994` must remain debug-only because current career owner is exact-registry quality
- `Istanbul 2020` must remain debug-only because its relevant career route is not `public_voice` in scope and its current owner is not a raw generic fallback case

## Required Tests

Future implementation should add:

1. flag-off no-op test
- with `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- and `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_VOICE_DETAIL_SUPPORT=false`
- public output must remain unchanged

2. `public_voice` detail eligibility test
- `fix04_h10_career_stellium`
- composed `public_voice` becomes `detail` eligible only when threshold passes

3. `public_voice` support eligibility test
- `tokyo_1998_06_21`
- `toronto_1976_06_26`
- support allowed only when `confidence >= 0.92` and owner quality is `raw_generic_fallback`

4. `public_main` disablement test
- even with all rollout flags on except main
- `public_main_eligible` stays `false`
- no `public_main` cluster replacement occurs

5. golden stability tests
- all accepted golden public outputs remain unchanged

6. exact-owner protection test
- `Istanbul 1997`
- exact public-voice registry owner must not be displaced by composed `public_voice`

7. customized-owner protection test
- if current owner quality is `customized_fallback_with_bespoke_copy`
- `public_voice` should not auto-promote beyond debug without explicit support threshold review

## Review Artifact Required After Future Implementation

If implementation happens later, generate:

`docs/system/batch_audits/v0_9a_1_public_voice_detail_support_post_rollout_review.md`

It should include:
- flag state
- affected charts
- before/after public surfaces
- which charts got `detail`
- which charts got `public_support`
- confirmation that `public_main` stayed off
- accepted golden no-op confirmation
- any false-positive or duplicate-support findings

## Rollout Recommendation

If a future implementation slice is approved, use this order:

1. `public_voice` -> `detail` only
- for:
  - `fix04_h10_career_stellium`
  - `tokyo_1998_06_21`
  - `toronto_1976_06_26`

2. run focused post-rollout review

3. only then consider `public_support`
- for the same three charts
- still with `public_main` disabled

## Final Verdict

`public_voice` is the only `career_route` subtype that currently looks plausible for a later controlled `detail/support` rollout.

Safe future candidates:
- `fix04_h10_career_stellium`
- `tokyo_1998_06_21`
- `toronto_1976_06_26`

Everything else in this scope remains debug-only for now.
