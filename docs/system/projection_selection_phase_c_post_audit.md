# Projection Selection Phase C Post Audit

Date: 2026-04-26  
Scope: post-Phase C selection QA (no code changes during audit)

Compared:
- Baseline: `Phase A+B post-audit` from `/tmp/projection_selection_policy_post_metrics.json`
- Current: `Phase C` from fresh runs, metrics at `/tmp/projection_selection_phase_c_post_metrics.json`

Fixtures (same 8 set):
- `fix01_leo_leo_classic`
- `fix02_capricorn_stellium`
- `fix03_pisces_cancer_water`
- `fix04_h10_career_stellium`
- `fix05_t_square_tense`
- `fix06_grand_trine_flow`
- `fix10_y2k_complex`
- `fix11_unknown_birthtime`

Method notes:
- Fresh payloads were generated from `interpret_natal_chart_ui` with `include_full_profile=true`.
- `SWISSEPH_PATH` was set to `/Users/sahradenizozdogan/Astrologi-Ai/backend/ephemeris` during measurement.
- `selected node_id changes` are computed against Phase A+B selected sets.

## 1) profile_narrative_projection_v1

| Metric | Phase A+B | Phase C | Delta | Status |
|---|---:|---:|---:|---|
| duplicate fingerprint total | 0 | 0 | 0 | neutral |
| near-duplicate summary pairs | 0 | 0 | 0 | neutral |
| domain union coverage | 7 | 7 | 0 | neutral |
| layer union coverage | 6 | 6 | 0 | neutral |
| repeated sentence pressure (types >=3) | 30 | 27 | -3 | improved |
| repeated sentence pressure (instances >=3) | 142 | 126 | -16 | improved |
| selected node_id changes vs A+B | n/a | 6/8 fixtures changed | n/a | needs tuning |
| avg added / removed node_ids vs A+B | n/a | +1.62 / -1.62 | n/a | needs tuning |
| traceability ratio | 1.0 | 1.0 | 0 | neutral |
| avg body chars | 362.27 | 359.05 | -3.22 | neutral |
| underfill count | 0 | 0 | 0 | neutral |

Classification: **improved**

Rationale:
- No regression in dedupe or coverage.
- Repetition pressure improved on both type and instance count.
- Main caution is selection churn (`6/8` fixture changed node set), but output quality metrics remained stable/improved.

## 2) profile_v8_projection_v1

| Metric | Phase A+B | Phase C | Delta | Status |
|---|---:|---:|---:|---|
| duplicate fingerprint total | 32 | 14 | -18 | improved |
| near-duplicate summary pairs | 40 | 14 | -26 | improved |
| domain union coverage | 6 | 7 | +1 | improved |
| layer union coverage | 4 | 6 | +2 | improved |
| repeated sentence pressure (types >=3) | 21 | 8 | -13 | improved |
| repeated sentence pressure (instances >=3) | 76 | 27 | -49 | improved |
| selected node_id changes vs A+B | n/a | 8/8 fixtures changed | n/a | needs tuning |
| avg added / removed node_ids vs A+B | n/a | +4.38 / -2.12 | n/a | needs tuning |
| traceability ratio | 1.0 | 1.0 | 0 | neutral |
| avg body chars | 255.31 | 334.41 | +79.10 | improved (richness) |
| v8 shadow dominance (avg shadow ratio) | not tracked | 0.03125 | n/a | improved |
| v8 shadow-dominant fixtures (>0.5) | not tracked | 0/8 | n/a | improved |
| underfill count | 0 | 0 | 0 | neutral |

Classification: **improved**

Rationale:
- Phase C removed a large part of duplication and near-duplicate pressure.
- Diversity improved (both domain and layer spread).
- No underfill, no traceability loss.
- Churn is high (`8/8` changed node sets), so coefficient tuning should focus on stability without losing dedupe gains.

## 3) Selected node_id change snapshot (vs A+B)

Narrative branch (changed fixtures):
- Changed: `fix01`, `fix03`, `fix04`, `fix06`, `fix10`, `fix11`
- Unchanged: `fix02`, `fix05`

V8 branch:
- Changed in all fixtures (`8/8`)

## 4) Overall classification

- `profile_narrative_projection_v1`: **improved**
- `profile_v8_projection_v1`: **improved**
- Global verdict: **improved, with coefficient stability tuning needed**

## 5) Recommendation

1. **Keep Phase C**: Yes. Core QA signals improved strongly, especially on v8 dedupe/repetition.
2. **Tune coefficients**: Yes, small targeted pass for stability/churn control.
3. **Partially revert A+B/C**: No. Current data does not justify revert.
4. **Add debug selection metrics next**: Yes (recommended).

Suggested debug metrics to add next (no schema change required in public output):
- candidate score decomposition (`base`, `similarity_penalty`, `domain_penalty`, `layer_penalty`, `repetition_penalty`)
- accepted/rejected reason counters by fixture and branch
- per-surface diversity counters (`domain_count`, `layer_count`, `duplicate_fp_hits`)
- churn trackers across runs for same fixture set
