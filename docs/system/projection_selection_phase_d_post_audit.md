# Projection Selection Phase D Post Audit

Date: 2026-04-26  
Scope: post-Phase D projection selection QA (no code changes in this audit)

Fixtures (same 8):
- `fix01_leo_leo_classic`
- `fix02_capricorn_stellium`
- `fix03_pisces_cancer_water`
- `fix04_h10_career_stellium`
- `fix05_t_square_tense`
- `fix06_grand_trine_flow`
- `fix10_y2k_complex`
- `fix11_unknown_birthtime`

Compared:
- Phase C baseline: `/tmp/projection_selection_phase_c_post_metrics.json`
- Phase D current: `/tmp/projection_selection_phase_d_post_metrics.json`

## 1) profile_narrative_projection_v1

| Metric | Phase C | Phase D | Delta | Status |
|---|---:|---:|---:|---|
| selected node_id changes | baseline | `0/8` changed | stable | neutral |
| duplicate fingerprint total | `0` | `0` | `0` | neutral |
| near-duplicate summary pairs | `0` | `0` | `0` | neutral |
| domain union coverage | `7` | `7` | `0` | neutral |
| layer union coverage | `6` | `6` | `0` | neutral |
| repeated sentence pressure (types >=3) | `27` | `27` | `0` | neutral |
| repeated sentence pressure (instances >=3) | `126` | `126` | `0` | neutral |
| traceability ratio | `1.0` | `1.0` | `0` | neutral |
| avg body chars | `359.05` | `359.05` | `0` | neutral |
| underfill count | `0` | `0` | `0` | neutral |

Summary:
- Narrative branch is unchanged by Phase D (expected, because Phase D targeted V8 behavior).

## 2) profile_v8_projection_v1

| Metric | Phase C | Phase D | Delta | Status |
|---|---:|---:|---:|---|
| selected node_id changes | baseline | `8/8` changed | high churn | needs tuning |
| avg add/remove vs Phase C | baseline | `+3.0 / -2.5` | high churn | needs tuning |
| duplicate fingerprint total | `14` | `10` | `-4` | improved |
| near-duplicate summary pairs | `14` | `10` | `-4` | improved |
| domain union coverage | `7` | `7` | `0` | neutral |
| layer union coverage | `6` | `6` | `0` | neutral |
| repeated sentence pressure (types >=3) | `8` | `5` | `-3` | improved |
| repeated sentence pressure (instances >=3) | `27` | `17` | `-10` | improved |
| traceability ratio | `1.0` | `1.0` | `0` | neutral |
| avg body chars | `334.41` | `335.72` | `+1.31` | neutral |
| underfill count | `0` | `0` | `0` | neutral |
| avg shadow ratio | `0.03125` | `0.53125` | `+0.50` | regression |

Summary:
- Dedup and repetition improved.
- Shadow distribution regressed hard (from shadow-light to shadow-dominant).

## 3) V8 Shadow Guardrail Checks

### 3.1 Shadow floor/cap behavior

- Floor (`>=1 shadow` in insight+differentiator set): `8/8` fixtures OK.
- Cap (`<=2 shadow` in insight+differentiator set): `0/8` fixtures OK.
- Per fixture selected shadow count in insight+differentiator set: `3` or `4`.

Interpretation:
- Floor works.
- Cap is not effective at set level in current behavior.

### 3.2 Shadow penalty share after guardrail

Measured from debug hook around `_apply_shadow_penalty_share_guardrail`:
- avg: `0.0`
- min: `0.0`
- max: `0.0`
- fixtures over `0.5`: `0`

Interpretation:
- Guardrail is over-damping shadow penalty to ~zero in practice.
- Combined with failed cap enforcement at set level, this produced shadow-heavy outputs.

## 4) Selected Role Balance (Inferable from Primary Layers)

Roles interpreted as:
- `hook` -> `recognition`
- `mechanism` -> `mechanism`
- `shadow` -> `shadow`
- `potential` -> `potential`
- `effect` -> `effect`

### 4.1 V8 role balance, Phase C vs Phase D

Inferred from selected node IDs mapped to current meaning_graph nodes.

| Role | Phase C total | Phase D total | Delta |
|---|---:|---:|---:|
| hook | `4` | `2` | `-2` |
| mechanism | `20` | `14` | `-6` |
| shadow | `2` | `34` | `+32` |
| potential | `7` | `2` | `-5` |
| effect | `28` | `10` | `-18` |

Fixture presence (out of 8):
- Phase C: `effect=8`, `mechanism=8`, `potential=7`, `hook=4`, `shadow=2`
- Phase D: `shadow=8`, `mechanism=8`, `effect=7`, `potential=2`, `hook=2`

Interpretation:
- Phase D shifts V8 strongly toward shadow-heavy selection, reducing potential/hook diversity.

## 5) Concrete Example Analysis

Example payload:
- `1996-12-28 07:10 Istanbul, TR`
- Fixture: `fix02_capricorn_stellium`

Selected nodes for `profile_v8_projection_v1`:

| Slot | node_id | title/headline | domain | primary_layer | layer_vector | why selected (debug) |
|---|---|---|---|---|---|---|
| `hero` | `mgv11_node_414ac9bd7fd11411` | `Neptün 1. Ev Shadow` | `general` | `shadow` | `[shadow:1.0]` | `stage=0, base=1.0, penalties=0, final=1.0` |
| `identity_axis` | `mgv11_node_5df860e5b67ecc4f` | `ASC Ruler: Satürn` | `general` | `mechanism` | `[mechanism:1.0]` | `stage=0, base=0.976, penalties=0, final=0.976` |
| `insight_strip[0]` | `mgv11_node_414ac9bd7fd11411` | `Neptün 1. Ev Shadow` | `general` | `shadow` | `[shadow:1.0]` | `stage=0, base=1.0, penalties=0, final=1.0` |
| `insight_strip[1]` | `mgv11_node_47939c5854144d15` | `Micro Insight` | `relationships` | `effect` | `[effect:1.0]` | `stage=0, base=0.996, penalties=0, final=0.996` |
| `insight_strip[2]` | `mgv11_node_d795bcabaaf7e12b` | `Ay 8. Ev Potential` | `emotional` | `potential` | `[potential:1.0]` | `stage=0, base=0.9744, penalties=0, final=0.9744` |
| `differentiators[0]` | `mgv11_node_4a0aaf3579c83b1a` | `Venüs 12. Ev Shadow` | `general` | `shadow` | `[shadow:1.0]` | `stage=0, base=1.0, penalties=0, final=1.0` |
| `differentiators[1]` | `mgv11_node_e76b44a170730e03` | `Ay 8. Ev Shadow` | `emotional` | `shadow` | `[shadow:1.0]` | `stage=0, base=1.0, penalties=0, final=1.0` |
| `differentiators[2]` | `mgv11_node_c1d664433b97a1de` | `Micro Insight` | `identity` | `recognition` | `[recognition:1.0]` | `stage=0, base=0.956, penalties=0, final=0.956` |

Observed issues in example:
- Same shadow node reused in `hero` and `insight_strip[0]`.
- Insight+differentiator shadow count = `4` (cap target `<=2` is violated).

## 6) Astrolog-like Checklist Match (same example)

Checklist:
- 1 hook / first impression
- 1 mechanism
- 1 tension/shadow
- 1 observable behavior/effect
- 1 potential/growth

Result:
- hook/first impression: ✅ (`hero` exists; `recognition` also present)
- mechanism: ✅ (`ASC Ruler: Satürn`)
- tension/shadow: ✅ (multiple shadow nodes)
- observable behavior/effect: ✅ (`Micro Insight` effect)
- potential/growth: ✅ (`Ay 8. Ev Potential`)

Note:
- Checklist passes, but composition is unbalanced (shadow over-represented).

## 7) Classification

- `profile_narrative_projection_v1`: **keep Phase D** (unchanged/stable)
- `profile_v8_projection_v1`: **tune coefficients**

Why not keep as-is:
- V8 shadow ratio regressed (`0.03125 -> 0.53125`)
- V8 cap behavior fails in all fixtures (`0/8`)
- role balance collapsed toward shadow channel

Why not partial revert yet:
- Dedupe and repetition improvements are real (`14->10`, `14->10`, repetition pressure down)

Final overall classification: **tune coefficients** (with V8 guardrail logic correction), **not ready for UI migration**.
