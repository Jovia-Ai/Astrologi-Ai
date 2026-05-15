# v0.9a Scoring and Opportunity Calibration Plan

Scope:
- planning only
- no code changes
- no runtime changes
- no public output changes
- no `detail/support/public_main` enablement

Source basis:
- `v0.9a` 50-chart debug-only metrics with:
  - `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
  - `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`
  - `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

## Decision Summary

Current `v0.9a` result is directionally strong but not rollout-ready beyond debug.

What is already working:
- `identity_route` generated `44` candidates
- `career_route` generated `40` candidates
- total `composed_vs_generic_fallback_opportunities` = `52`
- `career_route` opportunities = `34`
- `identity_route` opportunities = `18`
- accepted goldens remained public no-op
- no chart-fact safety issues were observed

What is not ready:
- `career_route` still over-produces low-confidence opportunities, especially under `strategic_role`
- `identity_route` still over-counts opportunities against chart-specific identity owners that are technically generic fallback clusters but semantically usable
- the current opportunity metric is too broad; it does not yet separate `raw_generic_fallback` from chart-specific or customized fallback strongly enough

Decision:
- do not roll out `detail/support` yet
- calibrate both `scoring` and `opportunity metrics` first

Recommended next implementation slice:
- `C) both`
- adjust scoring and opportunity metrics together
- do not roll out `detail/support` yet

## 1. Career Route Calibration

### Current distribution

Career candidate count: `40`

Career confidence / subtype shape:
- `strategic_role`: `10`
- `invisible_preparation_before_visibility`: `12`
- `public_voice`: `5`
- `action_initiative`: `4`
- `authority_responsibility`: `4`
- `creative_visibility`: `5`

Career opportunity count by subtype:
- `strategic_role`: `9`
- `invisible_preparation_before_visibility`: `10`
- `public_voice`: `4`
- `action_initiative`: `3`
- `authority_responsibility`: `3`
- `creative_visibility`: `5`

Low-confidence opportunities by subtype:
- `strategic_role`: `8`
- `invisible_preparation_before_visibility`: `3`

### Interpretation

`career_route` is the strongest debug-only family because it repeatedly identifies the right public-role/career hole when `public_main` is still owned by `career_career_visibility` or a close relative.

But it is also the family with the highest calibration risk:
- too many `strategic_role` hits are only weak structural MC/ruler/10H matches
- `invisible_preparation_before_visibility` is often semantically correct, but some cases still sit too close to a generic “behind the scenes” career guess

### True positives vs false positives

Likely true positives:
- `fix04_h10_career_stellium`
  - subtype: `public_voice`
  - confidence: `high`
  - this is the cleanest case of a composed career route outperforming raw generic visibility
- `kutahya_1959_10_21`
  - subtype: `creative_visibility`
  - confidence: `high`
  - mixed chart with clear public-role signal and weak current ownership
- `izmir_2007_07_19`
  - subtype: `authority_responsibility`
  - confidence: `high`
  - strong competence/public-role route that generic fallback is under-reading
- `tokyo_1998_06_21`
  - subtype: `public_voice`
  - confidence: `high`
- `toronto_1976_06_26`
  - subtype: `public_voice`
  - confidence: `high`

Likely false positives or too-early positives:
- `fix06_grand_trine_flow`
  - subtype: `strategic_role`
  - confidence: `low`
  - route exists, but not strong enough to justify opportunity priority
- `ankara_1993_06_10`
  - subtype: `strategic_role`
  - confidence: `low`
  - better treated as debug observation than rollout candidate
- `london_1972_12_30`
  - subtype: `strategic_role`
  - confidence: `low`
- `fix01_leo_leo_classic`
  - subtype: `strategic_role`
  - confidence: `low`
- `paris_1986_05_12`
  - subtype: `invisible_preparation_before_visibility`
  - confidence: `low`
  - meaningful but still too weak for any public use

### Calibration questions

When should `MC + ruler + 10H` count as `medium`?
- when all three are present
- when MC ruler is angular or in `10H/11H/12H`
- when at least one subtype-defining public planet signal is present:
  - Mercury -> `public_voice`
  - Saturn -> `authority_responsibility`
  - Venus/Neptune -> `creative_visibility`
  - Mars -> `action_initiative`
- when lived scene is specific enough to avoid generic visibility language

When is `career_route` too weak and should remain debug-only?
- when only MC + ruler exists without meaningful `10H` or public-angle reinforcement
- when subtype resolves only to `strategic_role` at `low` confidence
- when the route does not produce a scene more specific than generic visibility
- when a chart-specific exact career owner already exists and is semantically cleaner

Which evidence combinations justify later `detail/support` eligibility?
- `public_voice`
  - MC + ruler + Mercury or strong `10H Mercury`
- `authority_responsibility`
  - MC + ruler + Saturn + public/angular support
- `creative_visibility`
  - MC + ruler + Venus/Neptune + visible `10H` or public-angle emphasis
- `action_initiative`
  - MC + ruler + Mars or Mars-MC linkage
- `invisible_preparation_before_visibility`
  - MC + ruler + `12H` preparation signature plus concrete scene support

### Proposed scoring adjustments

Do not implement yet. Proposed direction:
- add a subtype penalty for `strategic_role` when no subtype-defining public planet is present
- require a stronger route bonus before `strategic_role` can reach `medium`
- keep `invisible_preparation_before_visibility` viable, but require both:
  - ruler in `12H` or equivalent backstage signature
  - visible career anchor beyond private planets alone
- give extra credit to:
  - `public_voice`
  - `authority_responsibility`
  - `creative_visibility`
  when their subtype-specific evidence is explicit

## 2. Identity Route Calibration

### Current distribution

Identity candidate count: `44`

Identity subtype distribution:
- `private_identity_spine`: `17`
- `direct_identity_spine`: `12`
- `controlled_identity_spine`: `6`
- `relational_identity_spine`: `6`
- `mediated_identity_spine`: `3`

Identity opportunity count by subtype:
- `private_identity_spine`: `7`
- `controlled_identity_spine`: `4`
- `direct_identity_spine`: `3`
- `relational_identity_spine`: `2`
- `mediated_identity_spine`: `2`

### Interpretation

`identity_route` is broad and stable as a debug family. It rarely looks unsafe.

Its problem is not raw generation quality. Its problem is opportunity over-counting.

The current metric still marks too many “identity opportunity” cases when the current identity owner is already chart-specific enough to be acceptable as a fallback owner.

Observed over-count pattern:
- the owner is still classified as `generic_fallback`
- but the actual `main_packet_id` is already a chart-specific exact-style anchor such as:
  - `gemini_asc_venus_1h_social_relational_presence_chart_exact`
  - `sun_aries_12h_hidden_private_fire_chart_exact`
  - `neptune_4h_soft_inner_presence_chart_exact`
  - `libra_asc_venus_chart_ruler_chart_exact`
  - `saturn_trine_pluto_deep_resilience_chart_exact`

This means the opportunity detector is mixing:
- true raw generic fallback
- chart-specific fallback owner with imperfect routing

### When should composed identity be a real replacement opportunity?

Only when:
- current owner is truly `raw_generic_fallback`
- owner scene is too generic or not clearly identity-spine-specific
- composed identity route has clearer `ASC + chart ruler + Sun` coherence
- composed candidate reaches at least `medium`
- lived scene is more identity-specific than the current owner

### When should it remain debug-only because exact identity owner is already strong?

Remain debug-only when:
- the current owner is exact/chart-specific, even if technical source typing still says `generic_fallback`
- the current owner already expresses the main identity spine with good lived-scene fit
- the composed identity route adds audit value but not public-surface value

Examples of likely over-counted identity opportunities:
- `adana_1998_09_12`
- `istanbul_2020_04_10`
- `fix02_capricorn_stellium`
- `madrid_2004_04_18`
- `new_york_1984_10_02`

Examples of more credible identity opportunities:
- `kutahya_1959_10_21`
- `izmir_2007_07_19`
- `mexico_city_1988_08_31`
- `cairo_1991_01_15`

### How should ASC + ruler + Sun conflict be handled?

If ASC, ruler, and Sun point in different directions:
- do not automatically treat this as a stronger identity opportunity
- use conflict to lower opportunity priority unless:
  - the conflict itself produces a coherent subtype
  - a distinct lived scene exists
  - the current owner clearly misses that tension

Recommended rule:
- conflict may support `debug` generation
- conflict alone should not support replacement opportunity

### Proposed narrowing rules

Do not implement yet. Proposed direction:
- identity opportunity should require current owner quality check, not source-type check alone
- down-rank opportunities where current owner `main_packet_id` already contains:
  - ASC/ruler identity anchor
  - explicit identity chart exact packet
  - already-good chart-specific identity scene
- require a higher threshold for opportunity under `private_identity_spine` unless the current owner is truly generic

## 3. Opportunity Definition Refinement

Current issue:
- `composed_vs_generic_fallback_opportunities` is too permissive
- it flags any domain-aligned generic public-main owner even when that owner is semantically acceptable

### Proposed taxonomy

#### `high_priority_opportunity`

Use only when:
- current owner is `raw_generic_fallback`
- current owner scene is generic/template-level
- composed candidate is chart-fact safe
- composed candidate has `medium` or `high` confidence
- composed candidate has stronger domain specificity and lived scene

#### `medium_priority_opportunity`

Use when:
- current owner is `customized_fallback_with_bespoke_copy`
- or current owner is chart-specific but semantically still misrouted
- composed candidate is useful, but not clearly urgent

#### `debug_observation_only`

Use when:
- current owner is `cluster_specific_fallback`
- or exact/chart-specific owner is already semantically acceptable
- or composed candidate is only `low` confidence
- or composed candidate adds audit visibility but not replacement value

### Priority rule

Opportunity should be high priority only when current owner is:
- `raw_generic_fallback`

Opportunity should be lower priority or excluded when current owner is:
- `customized_fallback_with_bespoke_copy`
- `cluster_specific_fallback`
- exact/chart-specific owner

## 4. Detail/Support Readiness

These are planning thresholds only. Do not enable them.

### `career_route` detail eligibility later

Minimum threshold:
- confidence `>= medium`
- subtype not `strategic_role` unless reinforced
- lived scene clearly more specific than generic visibility
- no stronger exact registry owner in same domain/public job

### `career_route` support eligibility later

Minimum threshold:
- confidence `>= medium`
- subtype-specific evidence present
- opportunity classified at least `medium_priority_opportunity`
- scene can support a public-support block without generic filler

### `identity_route` detail eligibility later

Minimum threshold:
- confidence `>= medium`
- current owner is not already a strong chart-specific identity owner
- lived scene expresses actual identity spine rather than just sign summary

### `identity_route` support eligibility later

Minimum threshold:
- confidence `>= high` by default
- or `medium` with clearly weak current identity owner
- opportunity is `high_priority_opportunity`, not just domain overlap

## 5. Representative Charts

### Best career true positives

1. `fix04_h10_career_stellium`
- subtype: `public_voice`
- confidence: `high`
- why it matters: cleanest proof that career route can beat raw generic visibility

2. `kutahya_1959_10_21`
- subtype: `creative_visibility`
- confidence: `high`
- why it matters: ordinary mixed chart with clear better-than-generic career signal

3. `izmir_2007_07_19`
- subtype: `authority_responsibility`
- confidence: `high`
- why it matters: real mixed chart with strong competence/public-role route

### Career low-confidence false positives

4. `fix06_grand_trine_flow`
- subtype: `strategic_role`
- confidence: `low`
- why it matters: route exists, but current opportunity classification is too optimistic

5. `ankara_1993_06_10`
- subtype: `strategic_role`
- confidence: `low`
- why it matters: useful debug candidate, weak replacement case

6. `london_1972_12_30`
- subtype: `strategic_role`
- confidence: `low`
- why it matters: should stay debug-only

### Identity over-counted opportunities

7. `adana_1998_09_12`
- current owner still gets counted as generic, but public identity owner is already semantically usable
- why it matters: accepted golden should not be treated as obvious replacement case

8. `istanbul_2020_04_10`
- composed identity exists, but current identity owner is already a chart-specific surface
- why it matters: opportunity metric is over-broad here

9. `fix02_capricorn_stellium`
- composed identity is strong, but current owner is not a simple raw generic fallback
- why it matters: scoring is fine; opportunity labeling is the problem

### Identity true opportunities

10. `kutahya_1959_10_21`
- identity route looks materially stronger than current generic owner

11. `izmir_2007_07_19`
- identity route likely adds real public value later

12. `mexico_city_1988_08_31`
- identity route appears clearer than the current fallback owner

## 6. Recommended Next Slice

Recommended answer:
- `C) both`

Meaning:
- adjust scoring
- adjust opportunity metrics
- do not roll out `detail/support` yet

Rationale:
- scoring alone will not fix over-counted identity opportunities
- opportunity taxonomy alone will not fix weak `career_route` subtype inflation
- both layers need calibration before any public-surface expansion is safe

## Final Readiness Verdict

`v0.9a` is successful as a debug-only semantic layer.

It is not yet ready for `detail/support` rollout.

The next strategic task is calibration:
- strengthen `career_route` subtype confidence logic
- narrow identity opportunity counting against already-acceptable chart-specific owners
- refine opportunity severity based on fallback quality, not source typing alone
