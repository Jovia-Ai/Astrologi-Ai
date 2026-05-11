# Projection Selection Debug Tuning Audit

Date: 2026-04-26  
Scope: debug-driven coefficient tuning audit (no code changes)

Compared surfaces:
- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

Fixture set (same 8):
- `fix01_leo_leo_classic`
- `fix02_capricorn_stellium`
- `fix03_pisces_cancer_water`
- `fix04_h10_career_stellium`
- `fix05_t_square_tense`
- `fix06_grand_trine_flow`
- `fix10_y2k_complex`
- `fix11_unknown_birthtime`

Artifacts:
- Debug metrics: `/tmp/projection_selection_debug_tuning_metrics.json`
- Phase A+B baseline: `/tmp/projection_selection_policy_post_metrics.json`

## 1) What Fired Most Often

## 1.1 profile_narrative_projection_v1 (overall)

- Decomposition rows: `1369`
- Accepted picks: `80`
- Penalty fire rates:
  - `similarity_penalty`: `34.04%`
  - `domain_penalty`: `2.85%`
  - `layer_penalty`: `2.26%`
  - `repetition_penalty`: `0.00%`
- Avg penalty per candidate:
  - similarity: `0.007205`
  - domain: `0.005128`
  - layer: `0.003170`
  - repetition: `0.000000`

Branch detail:
- `narrative_core`: similarity only meaningful (`14.82%`, avg `0.00251`)
- `narrative_extra`: similarity strongest (`48.74%`), then domain (`4.68%`) and layer (`3.72%`)

Interpretation:
- Narrative selection is mostly shaped by **similarity**; domain/layer caps are secondary.
- Repetition penalty is effectively inactive.

## 1.2 profile_v8_projection_v1 (overall)

- Decomposition rows: `2617`
- Accepted picks: `56`
- Penalty fire rates:
  - `similarity_penalty`: `48.15%`
  - `layer_penalty`: `38.14%`
  - `repetition_penalty`: `0.46%`
  - `domain_penalty`: `0.00%`
- Avg penalty per candidate:
  - similarity: `0.006792`
  - layer: `0.037891`
  - repetition: `0.000472`
  - domain: `0.000000`

Branch detail:
- `v8_hero`: layer penalty dominates (`35.04%` fire, avg `0.03422`), similarity inactive
- `v8_insight_strip`: similarity (`55.35%`) + layer (`38.82%`)
- `v8_differentiators`: similarity (`57.85%`) + layer (`38.53%`)

Interpretation:
- V8 is driven by **similarity + layer** penalties; domain penalty does not contribute.
- Layer penalty magnitude is much larger than similarity magnitude.

## 2) Too Strong / Too Weak Assessment

## 2.1 Similarity penalty

- Narrative: active and moderate; appears healthy.
- V8: active and useful, but not the dominant magnitude.
- `near_duplicate_hits` counter is `0` in both surfaces (thresholded hit metric is currently too conservative to be diagnostic).

Verdict: **keep** for now.

## 2.2 Domain penalty

- Narrative: low but non-zero contribution.
- V8: effectively `0` (never fires).

Verdict: **too weak/inactive for v8** (current v8 diversity is not coming from domain balancing).

## 2.3 Layer penalty

- Narrative: low-impact.
- V8: high-impact and dominant in removed-node analysis.

Critical evidence:
- `churn_removed_dominant_penalty` (v8): `{'layer_penalty': 17}`
- V8 shadow ratio shift (selected sets):
  - old Phase A+B avg: `0.59375`
  - current avg: `0.041667`
- Shadow component share inside layer penalty:
  - `shadow_penalty_component_sum / layer_penalty_sum_total = 93.56 / 99.16 = 94.35%`

Verdict: **too strong in v8 due shadow suppression**.

## 2.4 Repetition penalty

- Narrative: `0` fire.
- V8: near-zero (`0.46%` fire, tiny magnitude).

Verdict: **too weak/inactive** as a practical selector signal.

## 3) Are Strong Nodes Being Unfairly Rejected?

Heuristic used: “strong” = `base_score >= 0.85` and not selected.

## 3.1 Narrative

- Strong rejected nodes: `246`
- Penalized strong rejected: `125`
- High-penalty strong rejected (`sum penalties >= 0.1`): `0`
- Cases where `final_max < base_max`: `0`

Interpretation:
- Many strong nodes are unselected due capacity/ordering, not heavy penalty suppression.
- No strong evidence of unfair penalty rejection in narrative.

## 3.2 V8

- Strong rejected nodes: `263`
- Penalized strong rejected: `262`
- High-penalty strong rejected (`sum penalties >= 0.1`): `127`
- Cases where `final_max < base_max`: `130`

Representative rejected examples (all `base=1.0`, `final=0.9`, shadow-driven layer penalty `0.1`):
- `Satürn 1. Ev Shadow` (`mgv11_node_f663905c1b8cc547`)
- `Güneş Başak Shadow` (`mgv11_node_e54b298784f89707`)
- `Satürn 2. Ev Shadow` (`mgv11_node_764911665136dd89`)

Interpretation:
- In v8, strong-node rejection is frequently penalty-driven, mainly layer/shadow.

## 4) Churn Diagnosis

Compared against Phase A+B selected sets:
- Narrative changed fixtures: `5/8`
- V8 changed fixtures: `8/8`

Removed-node dominant penalty:
- Narrative: `layer_penalty (7)`, `similarity_penalty (4)`
- V8: `layer_penalty (17)`

Conclusion:
- V8 churn is not random; it is concentrated around **layer/shadow penalty pressure**.

## 5) Did V8 Diversity Gains Come from Healthy Selection?

Short answer: **partly no**.

Why:
- Domain diversity improved in outcome audits, but debug shows `domain_penalty` is inactive in v8 (`0.00%`).
- Most layer penalty mass is shadow-specific (`94.35%` share).
- Shadow representation dropped sharply (`~59%` to `~4%`).

Interpretation:
- Diversity gain is driven more by **shadow de-emphasis** than balanced multi-signal selection.

## 6) Recommendation

## 6.1 Keep / tune decision

- `profile_narrative_projection_v1`: **keep coefficients** (no urgent tuning)
- `profile_v8_projection_v1`: **tune specific coefficients**

## 6.2 What to tune (next pass, not implemented now)

1. Reduce v8 shadow component strength in `layer_penalty`.
2. Rebalance v8 so domain diversity is not shadow-suppression-dependent.
3. Keep similarity penalty close to current level (it is active but not excessive).
4. Repetition penalty can remain low priority unless repetition regresses again.

## 6.3 Guardrails to add before tuning rollout

1. Shadow-floor guardrail for v8 selection (prevent near-zero shadow presence across insight+differentiator set).
2. Penalty-share guardrail: shadow component should not dominate total layer penalty by extreme margins.
3. Churn guardrail: cap fixture-level selected-node churn vs previous stable baseline.
4. Add explicit “rejected_high_base” counters in debug (base high + not selected), so unfair rejection detection becomes first-class.

## 6.4 Final call

- **Do not keep coefficients as-is for v8**.
- **Tune specific coefficients + add guardrails**.
- **No change needed for narrative coefficients right now**.
