# Projection Selection Policy Post Audit

Date: 2026-04-26  
Scope: post-Phase A+B selection QA (no code changes)  
Compared outputs:
- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

## 1) Method

### Fixture set (same as Phase 1.7 baseline)
From `backend/tests/_fixtures/natal_v8_baseline.json`:
- `fix01_leo_leo_classic`
- `fix02_capricorn_stellium`
- `fix03_pisces_cancer_water`
- `fix04_h10_career_stellium`
- `fix05_t_square_tense`
- `fix06_grand_trine_flow`
- `fix10_y2k_complex`
- `fix11_unknown_birthtime`

### Baseline strategy
To compare **Phase 1.7 before selection policy** vs **after Phase A+B**:
1. Historical baseline metrics reused from:
   - `/private/tmp/projection_phase17_voice_audit_metrics_v2.json`
2. For new node-level metrics not stored historically (`selected node_id changes`, fingerprint/near-duplicate counts), pre-policy selection was replayed deterministically using the former selector logic (same graph inputs, same editorial generators).
3. After metrics were measured from fresh current `/interpret/ui` outputs (`include_full_profile=true`).

Metrics artifact generated in this audit:
- `/private/tmp/projection_selection_policy_post_metrics.json`

## 2) High-Level Result

Selection changed materially in both projection branches:
- `profile_narrative_projection_v1`: selected node set changed in **8/8 fixtures** (top slot changed in 6/8).
- `profile_v8_projection_v1`: selected node set changed in **8/8 fixtures** (top slot changed in 6/8).

Traceability remained intact:
- Narrative projection trace ratio: **1.0 → 1.0**
- Profile v8 projection trace ratio: **1.0 → 1.0**

## 3) Metric Comparison

## 3.1 profile_narrative_projection_v1

| Metric | Before (Phase 1.7) | After (Phase A+B) | Delta | Status |
|---|---:|---:|---:|---|
| Selected node count (avg) | 10.0 | 10.0 | 0.0 | neutral |
| Selected node changes (fixtures) | baseline | 8/8 changed | n/a | neutral |
| Duplicate fingerprint total | 0 | 0 | 0 | improved (kept clean) |
| Near-duplicate summary pairs total | 0 | 0 | 0 | improved (kept clean) |
| Domain union coverage | 7 | 7 | 0 | neutral |
| Layer union coverage | 6 | 6 | 0 | neutral |
| Avg body chars | 360.2 (replay) / 360.79 (historical) | 362.27 | +2.07 vs replay | neutral |
| Repeated sentence pressure (types >=3) | 32 (replay) / 31 (historical) | 30 | -2 vs replay | improved |
| Repeated sentence pressure (instances >=3) | 127 (replay) / 123 (historical) | 142 | +15 vs replay | regression |
| Traceability ratio | 1.0 | 1.0 | 0 | neutral |

Interpretation:
- Dedup cleanliness stayed strong.
- Coverage stayed stable.
- Repetition got more concentrated (fewer repeated templates, but more repeated instances).

## 3.2 profile_v8_projection_v1

| Metric | Before (Phase 1.7) | After (Phase A+B) | Delta | Status |
|---|---:|---:|---:|---|
| Selected node count (avg) | 8.0 | 8.0 | 0.0 | neutral |
| Selected node changes (fixtures) | baseline | 8/8 changed | n/a | neutral |
| Duplicate fingerprint total | 22 | 32 | +10 | regression |
| Near-duplicate summary pairs total | 28 | 40 | +12 | regression |
| Domain union coverage | 3 | 6 | +3 | improved |
| Layer union coverage | 5 | 4 | -1 | regression |
| Avg body chars | 256.37 (replay) / 255.36 (historical) | 255.31 | -1.06 vs replay | neutral |
| Repeated sentence pressure (types >=3) | 14 | 21 | +7 | regression |
| Repeated sentence pressure (instances >=3) | 59 | 76 | +17 | regression |
| Traceability ratio | 1.0 | 1.0 | 0 | neutral |

Interpretation:
- Domain spread improved.
- But semantic duplication and repetitive phrasing increased meaningfully in v8 projection.

## 4) Selected node_id Change Snapshot

Aggregate:
- Narrative projection:
  - avg added nodes per fixture: **3.12**
  - avg removed nodes per fixture: **3.12**
  - top-slot changed: **6/8**
- Profile v8 projection:
  - avg added nodes per fixture: **3.25**
  - avg removed nodes per fixture: **4.50**
  - top-slot changed: **6/8**

Representative fixtures:
- `fix02_capricorn_stellium` narrative: +3 / -3 (top changed)
- `fix11_unknown_birthtime` narrative: +5 / -5 (top changed)
- `fix01_leo_leo_classic` v8: +3 / -5 (top changed)
- `fix03_pisces_cancer_water` v8: +3 / -3 (top unchanged)

## 5) Editorial Quality Examples

## 5.1 Improvements observed

1. `fix01_leo_leo_classic` (`node_id: mgv11_node_dbc7ad23d4599e15`)
- After version keeps stronger contrast rhythm in body flow.
- Delta score (heuristic): `+35`.

2. `fix05_t_square_tense` (`node_id: mgv11_node_dc57bdd967ff8be9`)
- After version improves structure continuity (core -> context -> implication).
- Delta score (heuristic): `+33`.

3. `fix04_h10_career_stellium` (`node_id: mgv11_node_0e53c45130b9de3e`)
- After version gives cleaner shadow implication closure.
- Delta score (heuristic): `+16`.

## 5.2 Weak / regression examples

1. `fix05_t_square_tense` (`node_id: mgv11_node_a4f05212ae448695`)
- Before had stronger semantic progression; after collapses into weaker pacing.
- Delta score (heuristic): `-72`.

2. `fix04_h10_career_stellium` (`node_id: mgv11_node_0675c682af3e6ac1`)
- After loses nuance in the middle transition sentence.
- Delta score (heuristic): `-51`.

3. `fix11_unknown_birthtime` (v8 surface)
- Hero shifted:
  - before: `Merkür 11. ev Potansiyel`
  - after: `Satürn 1. ev Gölge`
- Selection emphasis became darker/tighter; not always editorially richer in top-card readability.

## 6) Regressions vs Legacy Nuance

Legacy nuance loss remains unresolved in narrative projection:
- `legacy profile_narrative` vs `after projection` body length gap:
  - average: **-28.74 chars**
  - worst: **-46.67 chars** (`fix10_y2k_complex`)

This indicates selection policy changes did not close the legacy editorial depth gap by themselves.

## 7) Classification

### profile_narrative_projection_v1
- improved: duplicate control remained clean, repeated type count slightly reduced
- neutral: coverage, traceability, body-length envelope
- regression: repeated sentence instance pressure increased
- **overall: needs tuning**

### profile_v8_projection_v1
- improved: domain coverage breadth
- neutral: traceability, body-length envelope
- regression: duplicate fingerprints, near-duplicate summaries, repeated sentence pressure, layer diversity drop
- **overall: regression (needs tuning)**

## 8) Conclusion

Phase A+B selection policy integration is **not a net quality win yet** for projection outputs:
- narrative branch: mixed, still usable, but repetition pressure needs tuning
- v8 branch: clear regression signals in duplication/repetition despite better domain spread

UI migration is **not recommended** at this stage.
