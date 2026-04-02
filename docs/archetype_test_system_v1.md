# Archetype Test System V1

Updated: 2026-04-02

## Goal
- Add one explicit archetype layer for natal profiles.
- Keep the current `natal_feature_graph -> primitive_engine_v2 -> master_selector` pipeline.
- Let the chart produce a deterministic `chart_prior`, then let the test refine it.
- Return a stable payload that mobile can render without reimplementing scoring logic.

## Why an API?
- The app already computes natal outputs on the backend, so archetype scoring should live in the same place.
- Mobile should not replicate chart math, primitive scoring, or fusion rules.
- A backend contract gives versioning, caching, analytics, rollout control, and one source of truth.
- If needed later, the same contract can also be used by web, admin tools, or experiments.

API here means:
- input: `birth data + test answers + confidence hints`
- output: `chart prior + test scores + fused archetypes + contradictions + confidence`

It does not mean the logic must be public. It is just the backend boundary for the app.

## Core Principle
- The chart should not directly declare a fixed personality type.
- The chart should produce weighted probabilities over archetypes.
- The test should measure the same latent structure from self-report behavior.
- Final output should be a fusion of both, not a winner-takes-all label.

Target output:
- `top_archetypes`: top 3 active archetypes
- `shadow_archetype`: the stress/protection expression
- `primary_contradiction`: the main inner tension
- `confidence`: how stable the result is

## Existing System Fit
- [backend/app/natal/narrative/natal_feature_graph.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/natal_feature_graph.py) already produces `public_private_split`, `contradiction_polarity`, and compensation signals.
- [backend/app/natal/narrative/primitive_engine_v2.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/primitive_engine_v2.py) already scores identity, regulation, relational, visibility, shadow, and compensation primitives.
- [backend/app/natal/narrative/master_selector.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/master_selector.py) already selects `primary_identity_spine`, `secondary_balancing_line`, `relational_line`, `work_visibility_line`, and `shadow_protection_line`.

This means the archetype system should be added as:

`chart -> primitives -> archetype chart prior -> test evidence -> fused archetype profile -> public render`

## Archetype Taxonomy
V1 should start with 8 archetypes, not 12. The current primitive system fits 8 more cleanly and reduces overlap.

### 1. Builder / Kurucu
- center: structure, responsibility, execution
- main primitives: `self_definition`, `inner_structure`, `methodical_drive`, `public_refinement`

### 2. Visionary / Vizyoner
- center: originality, future pull, meaning expansion
- main primitives: `originality_drive`, `big_picture_vision`, `meaningful_expansion`, `visible_presence`

### 3. Analyst / Analist
- center: pattern reading, mental architecture, precision
- main primitives: `mental_structuring`, `systems_thinking`, `tone_sensitivity`, `inner_structure`

### 4. Connector / Bag Kurucu
- center: social attunement, bonding, relational flow
- main primitives: `graceful_affection`, `relational_security`, `network_luck`, `visible_presence`

### 5. Guardian / Koruyucu
- center: safety, containment, repair, inner regulation
- main primitives: `recharge_through_home`, `family_self_reliance`, `emotional_threshold`, `relational_security`

### 6. Depthkeeper / Derinlik Tutucusu
- center: intensity, trust threshold, transformation through closeness
- main primitives: `intimacy_depth`, `transformative_bonding`, `emotional_threshold`, `backstage_creation`

### 7. Performer / Gorunen
- center: visibility, expression, charisma, audience energy
- main primitives: `visible_presence`, `public_refinement`, `creation_luck`, `network_luck`

### 8. Catalyst / Tetikleyici
- center: activation, change pressure, bold movement
- main primitives: `push_pull_drive`, `originality_drive`, `methodical_drive`, `self_definition`

## Test Design
The test should not ask users whether they "are a Builder" or "are deep". It should ask about behavior under preference, pressure, and relationship conditions.

V1 recommended format:
- 24 core items
- 6 adaptive items
- 5-point response scale
- 4 reverse-coded items
- 4 contradiction-pair items

Question families:
- `decision_style`
- `novelty_vs_structure`
- `visibility_preference`
- `stress_regulation`
- `closeness_boundary`
- `work_rhythm`
- `repair_style`
- `expression_style`

Each item should load onto:
- one primary archetype
- one secondary archetype or contradiction axis
- optionally one primitive for debug and retraining

## Scoring Model
The chart and test must score against the same archetype taxonomy.

### Step 1: Chart Prior
For each archetype:

```text
chart_prior[a] =
  sum(primitive_score[p] * archetype_primitive_weight[a][p])
  + slot_fit_bonus[a]
  + contradiction_bonus[a]
  + public_private_bonus[a]
```

Inputs:
- `primitive_scores`
- `identity_spine`
- `signature_contradictions`
- `public_private_split`

### Step 2: Test Score
For each archetype:

```text
test_score[a] =
  normalized_sum(item_response[i] * item_weight[i][a])
  - inconsistency_penalty[a]
```

Additional outputs:
- `answer_consistency`
- `social_desirability_risk`
- `axis_confidence`

### Step 3: Fusion
Default fusion:

```text
final_score[a] =
  0.55 * test_score[a] +
  0.35 * chart_prior[a] +
  0.10 * context_score[a]
```

Adaptive rules:
- if birth time is missing or low-confidence, lower chart weight
- if answer consistency is low, lower test weight
- if both are low-confidence, widen uncertainty and avoid hard labeling

### Step 4: Contradiction Output
Do not hide contradictions. Surface one main contradiction when strong enough.

Use existing candidates first:
- `structure_vs_originality`
- `visibility_vs_private_preparation`
- `closeness_vs_threshold`
- `composure_vs_internal_pressure`

## Result Construction
Recommended payload:

```json
{
  "engine_version": "archetype_profile_v1",
  "taxonomy_version": "archetype_taxonomy_v1",
  "fusion_version": "archetype_fusion_v1",
  "top_archetypes": [
    {
      "id": "builder",
      "label": "Kurucu",
      "score": 0.82,
      "source_split": {
        "chart_prior": 0.74,
        "test_score": 0.88,
        "context_score": 0.40
      }
    }
  ],
  "shadow_archetype": {
    "id": "guardian",
    "label": "Koruyucu",
    "score": 0.61
  },
  "primary_contradiction": {
    "id": "structure_vs_originality",
    "label": "Yapi kurarken ozgurluk ihtiyaci da canli kaliyor.",
    "score": 0.72
  },
  "confidence": {
    "global": 0.79,
    "chart": 0.81,
    "test": 0.76
  },
  "slots": {
    "primary_identity_spine": "builder",
    "secondary_balancing_line": "visionary",
    "relational_line": "depthkeeper",
    "work_visibility_line": "performer",
    "shadow_protection_line": "guardian"
  }
}
```

## Proposed API Contract
Recommended route:
- `POST /profile/archetype`
- `GET /profile/archetype/questions`

Request:

```json
{
  "birth_date": "1996-12-28",
  "birth_time": "07:10",
  "birth_place": "Istanbul, TR",
  "locale": "tr",
  "birth_time_confidence": "exact",
  "test_scores": {
    "builder": 0.82,
    "visionary": 0.61
  }
}
```

Current implementation note:
- The route accepts `test_scores` directly.
- It also accepts raw `answers` from the item bank when each answer carries `item_id`.
- Legacy direct `answers[].archetype_id` input still works as a fallback.
- `persist=true` stores the latest snapshot per authenticated user in `archetype_profiles`.
- If the same user opens the profile again with unchanged birth data and no new test input, the saved snapshot is returned instead of recomputing.

Response:
- `chart_prior`: raw chart-based archetype distribution
- `test_scores`: raw self-report distribution
- `top_archetypes`, `shadow_archetype`, `primary_contradiction`, `confidence`, `slots`: separate UI-ready blocks
- `ui_sections`: convenience grouping for rendering identity, protection, tension, and confidence panels
- `question_summary`: tells UI whether the test result exists and how many answers were used
- `snapshot`: tells UI whether the response was served from a persisted user snapshot
- `question_debug`: optional, only in debug

## Product Rules
- Never return only one archetype in public UI.
- Show top 3 archetypes.
- Show 1 shadow/protection archetype.
- Show 1 contradiction only if confidence passes threshold.
- If uncertainty is high, use softer copy such as `sende daha aktif gorunen cizgi`.

## V1 Rollout
1. Add taxonomy config.
2. Add fusion config.
3. Add item bank.
4. Build scorer using existing primitive outputs.
5. Add `POST /profile/archetype`.
6. Persist the latest fused result per user.
7. Add `GET /profile/archetype/questions`.
8. Render a compact archetype card group on profile.

## Research Notes
- Use the output as self-reflection, not clinical assessment.
- Avoid deterministic or diagnostic language.
- Archetype tests are usually multi-profile, not single-label.
- The chart should be framed as symbolic prior, not ground truth.
