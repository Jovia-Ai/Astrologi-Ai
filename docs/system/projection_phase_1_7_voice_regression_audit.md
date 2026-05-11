# Projection Phase 1.7 Voice Regression Audit

Date: 2026-04-24  
Scope: **Regression + voice-quality audit only** (no code changes) for:
- `legacy profile_narrative`
- `profile_narrative_projection_v1` (post Phase 1.7)
- `profile_v8_projection_v1` (post Phase 1.7)

## Method
- Ground truth source: fresh `POST /interpret/ui` payloads with `include_full_profile=true`.
- Fixture set: 8 representative charts from `backend/tests/_fixtures/natal_v8_baseline.json`:
  - `fix01_leo_leo_classic`
  - `fix02_capricorn_stellium`
  - `fix03_pisces_cancer_water`
  - `fix04_h10_career_stellium`
  - `fix05_t_square_tense`
  - `fix06_grand_trine_flow`
  - `fix10_y2k_complex`
  - `fix11_unknown_birthtime`
- Voice lens: `docs/voice/voice_spec.md` and `docs/voice/SHOU_BACKEND_UX_CONTRACT_v3.md`.
- Metrics artifacts:
  - `/tmp/projection_phase17_voice_audit_metrics_v2.json`
  - `/tmp/projection_phase17_voice_audit_metrics.json` (discarded due sentence-split bug)

## Comparison Snapshot (Aggregate)

| Surface | Avg body chars | Avg sentence count | Repeated sentence pressure (3+ repeats) | Generic banned phrase hits | Motivational hits |
|---|---:|---:|---:|---:|---:|
| `legacy profile_narrative` | 391.45 | 4.00 | 17 repeated sentence types / 77 repeated instances | n/a | n/a |
| `profile_narrative_projection_v1` | 360.79 | 4.00 | 31 repeated sentence types / 123 repeated instances | 0 | 0 |
| `profile_v8_projection_v1` | 255.36 | 2.72 | 14 repeated sentence types / 59 repeated instances | 0 | 0 |

Notes:
- Projection narrative is no longer short; length is close to legacy.
- Repetition pressure is **higher** than legacy in projection outputs.

## Check-by-check Findings

### 1) Meaning-graph traceability preserved?
Verdict: **Yes (strong).**
- `profile_narrative_projection_v1` block traceability ratio: **1.00** across all 8 fixtures.
- `profile_v8_projection_v1` hero/identity/differentiator trace objects: present and valid in all sampled payloads.

### 2) Generic or motivational language introduced?
Verdict: **Mostly controlled, but not clean.**
- Banned generic phrases (Phase 1.7 targets) occurrences: **0**
  - `"Bu hikayenin merkezinde şu var"`: 0
  - `"Zorlayan tarafı şu"`: 0
  - `"En belirgin etkisini"`: 0
  - `"Sende öne çıkan dinamik şu"`: 0
  - `"Temel tonun burada netleşiyor"`: 0
- Motivational/self-help lexicon:
  - motivational regex hits: **0**
  - self-help-ish hits: **5** (`"dayanıklılık ve strateji"` cluster)

### 3) Turkish naturalness (specific, non-robotic)?
Verdict: **Improved vs pre-1.7, but still templated.**
- Improvements:
  - raw labels cleaned (`Identity.`, `Mind.` -> normalized) hit count: **0**
  - `"alan alanında"` duplication: **0**
- Remaining naturalness regressions:
  - Locale/casing bug: `"Ilişkilerde"` appears **4** times (ASCII `I`).
  - Recurrent boilerplate sentence endings:
    - `"Özellikle ... sonucu belirleyen ana kaldıraç olur"` (26 hits)
    - `"kararlarının arka planında bu tema güçlü kalır"` (26 hits)
    - `"günlük akışta ..."` (33 hits)

### 4) cause/mechanism/effect/shadow/potential distinctions preserved?
Verdict: **Partially preserved.**
- Projection layer coverage vs same payload `meaning_graph_v1_1`:
  - Average ratio: **0.871**
  - Min/Max: **0.667 / 1.0**
- Pattern:
  - `mechanism/effect/potential/shadow` are consistently represented.
  - `cause` and `recognition` are sometimes underrepresented in selected projection blocks.

### 5) Misleading / too broad / self-help drift?
Verdict: **Low-to-medium risk (localized).**
- Detected drift is mostly from repeated uplift templates, not explicit motivational coaching.
- Weak examples include over-broad implications:
  - `"Özellikle ... ana kaldıraç olur"` with weak semantic specificity.
  - `"dayanıklılık ve strateji"` phrasing (reads strategy-coaching on some blocks).

### 6) Body length increased without nuance?
Verdict: **Partly yes.**
- Length increased and is healthy in raw size, but nuance gain is uneven:
  - projection bodies with context cue: **1.00**
  - projection bodies with implication cue: **0.662**
  - bodies satisfying context+implication together: **0.662**
- So output got longer and structurally fuller, but ~34% still miss strong implication depth.

### 7) Deterministic outputs?
Verdict: **Yes.**
- Re-run equality checks on fresh payload for two fixtures:
  - `profile_narrative_projection_v1`: equal across repeated runs
  - `profile_v8_projection_v1`: equal across repeated runs

### 8) Schema and public keys unchanged?
Verdict: **Yes (no schema drift detected).**
- `public` key-set stable across all 8 fixtures.
- `profile_narrative_projection_v1.profile_public` key-set stable:
  - `blocks`, `core_blocks`, `detail_cards`, `extra_blocks`, `schema_version`
- `profile_v8_projection_v1` key-set stable:
  - `version`, `source_graph_version`, `source_graph`, `hero`, `identity_axis`, `insight_strip`, `differentiators`, `traceability`

### 9) Regressions vs Phase 1.5?
Verdict: **Mixed (clear wins + clear regressions).**

Wins vs Phase 1.5:
- Generic phrase artifacts targeted in 1.7 are cleaned (0 hits).
- Raw label leakage removed (0 hits).
- Traceability and determinism remain intact.

Regressions / unresolved risks vs Phase 1.5:
- Repetition pressure increased at corpus level (more repeated sentence templates).
- Turkish casing artifact (`Ilişkilerde`) persists.
- `profile_v8_projection_v1` remains structurally shallow vs legacy `profile_v8` (effective completeness still ~0.25 in content surface terms).

## Quality Examples

### Strong examples (projection)
1. `fix02_capricorn_stellium` — `Ay 8. ev Gölge`  
`Gerilim yükseldiğinde ... Fark edilmediğinde ... sınır zekasına dönüşür.`

2. `fix04_h10_career_stellium` — `Mars 10. ev Gölge`  
`Gerilim arttığında ... Yönetilmediğinde ... netlik ve dayanıklılık sağlar.`

3. `fix11_unknown_birthtime` — `Neptün 2. ev`  
Specific core meaning + context + implication sequence stays coherent.

### Weak examples (projection)
1. `fix11_unknown_birthtime` — `Micro Insight`  
Contains `"dayanıklılık ve strateji"` coaching-like drift.

2. `fix02_capricorn_stellium` — `Zihinsel ritmin`  
Ends with generic `"ana kaldıraç"` formula; nuance flattens.

3. `fix02_capricorn_stellium` — `Görünür olma ritmin`  
Contains `"Ilişkilerde"` casing artifact + repeated scaffold cadence.

## Final Classification

### Overall
- **needs tuning**

### By output branch
- `profile_narrative_projection_v1`: **needs tuning**  
  Reason: voice now richer and compliant on major banned phrases, but still templated with repetition and implication flattening in a non-trivial subset.

- `profile_v8_projection_v1`: **needs tuning**  
  Reason: traceable and deterministic, but editorial/completeness depth is still below legacy profile contract.

### Revert recommendation
- **should revert fully:** No
- **should revert partially:** Not required for stability; targeted micro-copy tuning is safer than rollback.

