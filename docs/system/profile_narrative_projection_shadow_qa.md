# Profile Narrative Projection Shadow QA (Broad)

Date: 2026-04-24  
Scope: `profile_narrative` vs `profile_narrative_projection_v1` only.  
Constraints followed: no code changes, no UI migration, no `profile_v8_projection_v1` work.

## Fixture Set

Source: `backend/tests/_fixtures/natal_v8_baseline.json`  
Used fixtures (10):
- `fix01_leo_leo_classic`
- `fix02_capricorn_stellium`
- `fix03_pisces_cancer_water`
- `fix04_h10_career_stellium`
- `fix05_t_square_tense`
- `fix06_grand_trine_flow`
- `fix07_aries_libra_nodes`
- `fix08_cancer_capricorn_nodes`
- `fix09_edge_cusp_planet`
- `fix10_y2k_complex`

## Method

- Generated fresh natal public payloads via backend route function `interpret_natal_chart_ui(...)` with `include_full_profile=true` and `locale=tr` for each fixture.
- Compared:
  - `public.profile_narrative.profile_public`
  - `public.profile_narrative_projection_v1.profile_public`
- Metrics computed per fixture:
  - avg body chars
  - avg detail blocks/card
  - domain coverage
  - layer coverage
  - traceability ratio
  - repeated phrase / flatness indicators
- Traceability definition (projection): block has valid `node_id` + matching `trace.node_id`; evidence ratio also tracked.
- Legacy does not expose explicit meaning-graph domain/layer ontology; legacy domain proxy used from `category_support.family`.

## Aggregate Results (10 Fixtures)

| Metric | Legacy `profile_narrative` | Projection `profile_narrative_projection_v1` |
|---|---:|---:|
| Avg body chars | 388.4 | 199.1 |
| Avg detail blocks/card | 6.79 | 3.29 |
| Avg sentences/body | 4.00 | 2.73 |
| Domain coverage (avg count) | 6.4 family proxies | 5.5 graph domains |
| Layer coverage (avg count) | N/A (no explicit layer field) | 5.1 (`all layers`) |
| Traceability ratio | 1.00 proxy (astro/category support) | 1.00 |
| Traceability with evidence | N/A | 1.00 |
| Repeated opening ratio | 0.00 | 0.20 |
| Repeated body ratio | 0.00 | 0.00 |
| Template context sentence ratio | N/A | 0.74 |
| Short body ratio (`<160`) | 0.00 | 0.60 |
| Lexical diversity | 0.617 | 0.477 |

Projection union domain coverage across set:
- `career`, `emotional`, `general`, `identity`, `life_direction`, `mind`, `relationships`

Projection union layer coverage across set:
- `cause`, `effect`, `mechanism`, `potential`, `recognition`, `shadow`

## Per-Fixture Snapshot

| Fixture | Legacy Avg Body | Projection Avg Body | Legacy Avg Detail | Projection Avg Detail | Projection Domains | Projection Layers | Projection Trace | Template Ratio | Short Body Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fix01_leo_leo_classic | 392.4 | 202.6 | 7.00 | 3.20 | 5 | 4 | 1.00 | 0.70 | 0.40 |
| fix02_capricorn_stellium | 383.4 | 248.8 | 6.83 | 3.50 | 6 | 5 | 1.00 | 0.60 | 0.40 |
| fix03_pisces_cancer_water | 393.4 | 222.5 | 6.75 | 3.40 | 5 | 5 | 1.00 | 0.70 | 0.50 |
| fix04_h10_career_stellium | 396.6 | 164.7 | 6.67 | 3.30 | 6 | 6 | 1.00 | 0.90 | 0.90 |
| fix05_t_square_tense | 387.6 | 184.5 | 6.67 | 3.40 | 6 | 5 | 1.00 | 0.80 | 0.70 |
| fix06_grand_trine_flow | 390.4 | 174.7 | 6.75 | 3.30 | 5 | 6 | 1.00 | 0.80 | 0.70 |
| fix07_aries_libra_nodes | 381.3 | 179.8 | 6.75 | 3.10 | 5 | 6 | 1.00 | 0.80 | 0.70 |
| fix08_cancer_capricorn_nodes | 389.9 | 198.0 | 6.83 | 3.20 | 5 | 5 | 1.00 | 0.70 | 0.50 |
| fix09_edge_cusp_planet | 377.6 | 204.0 | 6.92 | 3.30 | 6 | 4 | 1.00 | 0.80 | 0.70 |
| fix10_y2k_complex | 391.6 | 211.2 | 6.75 | 3.20 | 6 | 5 | 1.00 | 0.60 | 0.50 |

## Repeated Phrase / Flatness Indicators

- Projection bodies are structurally consistent but still templated:
  - `Bu tema en çok` appears in 74/100 projection blocks.
  - `katmanında çalışıyor` appears in 74/100 projection blocks.
- Repeated opening ratio is 0.20 on projection (legacy: 0.00).
- 60% of projection bodies are under 160 chars.
- Projection lexical diversity is materially lower than legacy (0.477 vs 0.617).

Interpretation:
- Traceability and semantic coverage are strong.
- Editorial variance and depth are still below legacy narrative quality.

## Missing Important Nuance Examples

1. `fix08_cancer_capricorn_nodes`
- Legacy headline: `Karar verirken içinde ne oluyor` (family: `mind`)
- Legacy body carries a multi-step arc (observed pattern -> daily behavior -> contextual impact).
- Projection headline: `Micro Insight` (domain: `mind`)
- Projection body is concise but compressed, losing pacing/contrast nuance.

2. `fix04_h10_career_stellium`
- Legacy headline: `Cümlelerinin arkası` (family: `mind`)
- Legacy body includes social-context framing and contradiction rhythm.
- Projection headline: `ASC Ruler: Merkür` (domain: `mind`)
- Projection body preserves core semantic signal but drops editorial progression and relational context.

3. `fix01_leo_leo_classic`
- Legacy headline: `İlk hissedilen şey` (family: `identity`)
- Legacy body includes outer impression vs inner anchor dual framing.
- Projection headline: `Micro Insight` (domain: `identity`)
- Projection body remains traceable but flattens into a shorter, single-angle statement.

## QA Verdict

Decision: **still shadow-only; needs another editorial tuning pass** (not ready for limited internal canary yet).

Why:
- Strong points:
  - Traceability quality is production-strong (`1.00` with node and evidence linkage).
  - Domain/layer coverage is broad and stable across diverse fixtures.
- Blocking gaps:
  - Editorial depth remains substantially behind legacy (`199` vs `388` avg chars; `3.29` vs `6.79` detail blocks/card).
  - Flatness risk is still high (template sentence ratio `0.74`, short-body ratio `0.60`).
  - Narrative pacing and relational/context nuance are not yet at canary quality.

## Notes

- During generation, Swiss Ephemeris warnings were observed for missing `seas_18.se1` (Chiron/Juno path). Payloads still produced successfully for all fixtures, but this environment issue should be tracked separately from projection parity.
