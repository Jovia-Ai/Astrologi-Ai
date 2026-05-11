# Projection Selection Readiness Audit

Date: 2026-04-26  
Scope: same 8-fixture set (`fix01`, `fix02`, `fix03`, `fix04`, `fix05`, `fix06`, `fix10`, `fix11`) and same two branches:
- `profile_narrative_projection_v1`
- `profile_v8_projection_v1`

Compared phases:
1. Phase 1.7 baseline
2. Phase C
3. Phase D guardrail-fixed (current)

## Data sources
- Phase 1.7 baseline + Phase A/B transition artifact: `/tmp/projection_selection_policy_post_metrics.json`
- Phase C artifact: `/tmp/projection_selection_phase_c_post_metrics.json`
- Current (guardrail-fixed) fresh run: `/tmp/projection_selection_readiness_metrics.json`
- Supplemental V8 cap/floor verification (current): `/tmp/projection_selection_phase_d_guardrails_fix_metrics.json`

Note:
- Some Phase 1.7 and Phase C fields were not historically logged (`avg_shadow_ratio` for narrative; Phase 1.7 `node_id reuse`). These are marked `n/a`.

## 1) Phase comparison

### 1.1 `profile_narrative_projection_v1`

| Metric | Phase 1.7 baseline | Phase C | Phase D guardrail-fixed current |
|---|---:|---:|---:|
| duplicate fingerprint total | 0 | 0 | 0 |
| near-duplicate total | 0 | 0 | 0 |
| repeated sentence pressure (types/instances, 3+) | 32 / 127 | 27 / 126 | 27 / 126 |
| domain coverage (union) | 7 domains | 7 domains | 7 domains |
| layer coverage (union) | 6 layers | 6 layers | 6 layers |
| avg shadow ratio | n/a | n/a | 0.375 |
| node_id reuse total | n/a | 0 | 0 |
| traceability ratio avg | 1.0 | 1.0 | 1.0 |
| avg body chars | 360.79 | 359.05 | 359.05 |
| selected node churn vs previous stable baseline | 0/8 | 6/8 (+1.62/-1.62) | 0/8 (+0/-0) vs Phase C |

Summary:
- Narrative selection is stable and clean in current output (no dup/near-dup/reuse regressions).
- Main unresolved issue remains voice repetition pressure, not selection correctness.

### 1.2 `profile_v8_projection_v1`

| Metric | Phase 1.7 baseline | Phase C | Phase D guardrail-fixed current |
|---|---:|---:|---:|
| duplicate fingerprint total | 22 | 14 | 0 |
| near-duplicate total | 28 | 14 | 0 |
| repeated sentence pressure (types/instances, 3+) | 14 / 59 | 8 / 27 | 8 / 25 |
| domain coverage (union) | 3 domains | 7 domains | 7 domains |
| layer coverage (union) | 5 layers | 6 layers | 6 layers |
| avg shadow ratio | n/a | 0.03125 | 0.234375 |
| node_id reuse total (cross-slot) | n/a | 14 | 0 |
| traceability ratio avg | 1.0 | 1.0 | 1.0 |
| avg body chars | 255.36 | 334.41 | 256.36 |
| selected node churn vs previous stable baseline | 0/8 | 8/8 (+4.38/-2.12) | 8/8 (+2.38/-0.62) vs Phase C |

Summary:
- Selection quality improvements are strong in current output: dedupe, near-dup, cross-slot reuse all improved to zero.
- Shadow balance is now in target band at aggregate level (`~0.23`) and guardrails pass in the cap/floor audit.
- Churn remains high vs Phase C (all fixtures changed), but magnitude dropped (avg removals decreased from `2.12` to `0.62`).

## 2) Current guardrail checks (V8)

From current run + guardrail verification:
- shadow cap pass rate (`<=2` in insight_strip+differentiators): **8/8**
- shadow floor pass rate (`>=1` when shadow candidates exist): **8/8**
- cap+floor combined pass rate: **8/8**
- duplicate node_id across V8 slots: **0**
- duplicate fingerprint total: **0**
- near-duplicate total: **0**
- traceability: **1.0**
- underfill: **0**

## 3) 5 best examples (current)

1. `fix02_capricorn_stellium` — `profile_narrative_projection_v1`  
   Why: high semantic spread (`6 domain / 5 layer`), clean dedupe, strong body depth.  
   Sample: “... dışarıdan sakin ama belirleyici ... içeride yoğun bir değerlendirme ...”

2. `fix04_h10_career_stellium` — `profile_narrative_projection_v1`  
   Why: strong coverage (`6 / 5`), no duplication artifacts, good tension+implication cadence.

3. `fix10_y2k_complex` — `profile_narrative_projection_v1`  
   Why: stable traceability and broad domain spread with low flattening risk.

4. `fix05_t_square_tense` — `profile_v8_projection_v1`  
   Why: shadow ratio in healthy range (`0.25`), `5 domain / 4 layer`, zero slot reuse.

5. `fix04_h10_career_stellium` — `profile_v8_projection_v1`  
   Why: balanced slot composition, clean dedupe, stable traceability.

## 4) 5 weakest examples (current)

1. `fix11_unknown_birthtime` — `profile_v8_projection_v1`  
   Weakness: shadow ratio low (`0.125`), narrower semantic spread (`4 domain / 3 layer`), shortest average copy.

2. `fix06_grand_trine_flow` — `profile_v8_projection_v1`  
   Weakness: limited layer diversity (`3`), still voice-flat in some blocks.

3. `fix01_leo_leo_classic` — `profile_v8_projection_v1`  
   Weakness: acceptable selection integrity but still template-visible wording in micro bodies.

4. `fix11_unknown_birthtime` — `profile_narrative_projection_v1`  
   Weakness: higher repetition pressure and lower coverage (`4 domain / 4 layer`) vs stronger fixtures.

5. `fix05_t_square_tense` — `profile_narrative_projection_v1`  
   Weakness: repetition pressure locally high despite good semantic coverage.

## 5) Readiness classification

By branch:
- `profile_narrative_projection_v1`: **ready for shadow monitoring only**
- `profile_v8_projection_v1`: **needs voice tuning** (selection quality is much healthier, but copy quality is still uneven)

Overall:
- **needs voice tuning**

Rationale:
- Selection integrity is now strong (especially V8 dedupe/reuse/cap-floor behavior).
- Voice quality is still the limiting factor (template pressure, uneven richness in weak fixtures).
- Public UI migration is **not** recommended yet.

## 6) Recommendation

1. Keep current selection guardrails (no rollback).
2. Run next pass as voice/micro-copy tuning, not selection rewrite.
3. Continue shadow monitoring with this exact 8-fixture pack before any internal canary expansion.
