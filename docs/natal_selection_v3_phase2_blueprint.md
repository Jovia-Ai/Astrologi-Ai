# Natal Selection V3 Phase 2 Blueprint

Updated: 2026-04-02

## Goal
- Turn Phase 1 signals into one deterministic identity selection contract.
- Keep current natal richness.
- Reduce multi-voice behavior before surface migration.

This document defines:
- Master Selector scoring model
- primitive-to-line candidate mapping
- contradiction taxonomy v1
- layer arbitration rules
- rollout flag plan

## 1. Master Selector Contract

Add or evolve:
- `backend/app/natal/narrative/master_selector.py`

Target output:

```python
{
    "engine_version": "master_selector_v1",
    "primary_identity_spine": {},
    "secondary_balancing_line": {},
    "relational_line": {},
    "work_visibility_line": {},
    "shadow_protection_line": {},
    "candidate_pool": {},
    "selection_debug": {},
}
```

Each selected line should contain:

```python
{
    "line_id": "identity_structure_with_originality",
    "family": "identity",
    "label": "controlled originality",
    "score": 0.81,
    "confidence": 0.78,
    "source_primitives": ["inner_structure", "originality_drive"],
    "supporting_features": ["chart_ruler_centrality", "house_ruler_recursion"],
    "supporting_motifs": ["identity_structure", "visionary_originality"],
    "counterweights": ["structure_vs_originality"],
    "evidence": [],
}
```

## 2. Selection Pipeline

Selector input order:

`natal_feature_graph_v2 -> primitive_engine_v2 -> contradiction_engine -> line candidates -> line ranking -> final spine selection`

Selector should not read phrase libraries.
Phrase libraries remain render inventory, not selection authority.

## 3. Line Families

The selector should always try to fill these slots:
- `primary_identity_spine`
- `secondary_balancing_line`
- `relational_line`
- `work_visibility_line`
- `shadow_protection_line`

Fallback rule:
- If a slot cannot be filled with confidence >= `0.52`, emit best candidate with `fallback_used=True`.

## 4. Primitive-To-Line Mapping

### Primary Identity Spine
Highest priority primitives:
- `self_definition`
- `inner_structure`
- `originality_drive`
- `big_picture_vision`
- `visible_presence`
- `mental_structuring`
- `meaningful_expansion`

Common composite line examples:
- `self_definition + inner_structure`
- `inner_structure + originality_drive`
- `self_definition + visible_presence`
- `big_picture_vision + meaningful_expansion`
- `mental_structuring + systems_thinking`

### Secondary Balancing Line
Highest priority primitives:
- `originality_drive`
- `systems_thinking`
- `methodical_drive`
- `recharge_through_home`
- `backstage_creation`
- `visible_presence`
- `big_picture_vision`

Purpose:
- modify or balance the main spine
- explain how the person differs from a flat reading of the primary line

### Relational Line
Highest priority primitives:
- `intimacy_depth`
- `relational_security`
- `graceful_affection`
- `transformative_bonding`
- `emotional_threshold`

### Work / Visibility Line
Highest priority primitives:
- `public_refinement`
- `visibility_sensitivity`
- `visible_presence`
- `creation_luck`
- `network_luck`
- `backstage_creation`

### Shadow / Protection Line
Highest priority primitives:
- `inner_critic`
- `push_pull_drive`
- `emotional_threshold`
- `tone_sensitivity`
- `recharge_through_home`
- `family_self_reliance`
- `backstage_creation`

## 5. Candidate Generation

Master selector should not only rank single primitives.
It should generate line candidates in 3 classes:

### Single-Primitive Candidates
Use when one primitive is unusually dominant.

Example:
- `inner_structure`

### Dual-Primitive Candidates
Default class.

Example:
- `inner_structure + originality_drive`
- `intimacy_depth + emotional_threshold`

### Primitive + Contradiction Candidates
Use when contradiction is central enough to define the line.

Example:
- `visible_presence + visibility_vs_private_preparation`
- `intimacy_depth + closeness_vs_threshold`

## 6. Scoring Model

### Candidate Score

Suggested formula:

```python
candidate_score =
    primitive_core * 0.34
    + primitive_support * 0.16
    + feature_support * 0.16
    + motif_support * 0.12
    + contradiction_bonus * 0.10
    + salience_bonus * 0.06
    + role_fit_bonus * 0.06
    - redundancy_penalty * 0.08
    - incoherence_penalty * 0.08
```

### Component Definitions

`primitive_core`
- top primitive score in the candidate

`primitive_support`
- mean score of secondary primitives in the candidate

`feature_support`
- feature graph support from:
  - `chart_ruler_centrality`
  - `luminary_condition`
  - `angular_dominance`
  - `house_ruler_recursion`
  - `dispositor_chain_pressure`
  - `exact_aspect_salience`
  - `public_private_split`

`motif_support`
- support from `natal_graph_v2.signature_motifs`

`contradiction_bonus`
- non-zero only if contradiction is psychologically central and compatible with the slot

`salience_bonus`
- derived from `planet_salience`

`role_fit_bonus`
- slot-specific fit

`redundancy_penalty`
- penalize candidates too similar to already selected lines

`incoherence_penalty`
- penalize candidates that fight the current primary line without contradiction framing

### Confidence

Suggested formula:

```python
confidence =
    feature_support * 0.35
    + motif_support * 0.20
    + contradiction_resolution * 0.15
    + cross_signal_agreement * 0.30
```

`cross_signal_agreement` means:
- primitive score direction agrees with feature graph
- motif evidence agrees with line family
- no strong opposing contradiction is unresolved

## 7. Slot-Specific Fit Rules

### Primary Identity Spine
Boost if:
- linked to chart ruler
- linked to ASC / 1st house
- linked to Sun or Moon condition
- repeated across motif + primitive + salience layers

Penalize if:
- only supported by one narrow placement
- mostly relational or situational

### Secondary Balancing Line
Boost if:
- it explains the main spine’s modifier
- it introduces real nuance without competing with the primary

Penalize if:
- it is just a weaker clone of the primary

### Relational Line
Boost if:
- 7th / 8th / Moon / Venus / Saturn relationship signals align

Penalize if:
- mainly work/identity coded

### Work / Visibility Line
Boost if:
- MC / 10th / Sun / Saturn / Jupiter / public-private signals align

### Shadow / Protection Line
Boost if:
- contradiction score is high
- primitive is protection/regulation/shadow coded
- public story would feel incomplete without it

## 8. Contradiction Taxonomy V1

Add or evolve:
- `backend/app/natal/narrative/contradiction_engine.py`

Contradictions should be system objects with:

```python
{
    "id": "structure_vs_originality",
    "family": "identity_tension",
    "left": "inner_structure",
    "right": "originality_drive",
    "score": 0.73,
    "editorial_label": "structured originality",
    "priority": "high",
}
```

### Contradiction Families

#### Identity Tension
- `structure_vs_originality`
- `visibility_vs_private_preparation`
- `confidence_vs_internal_pressure`

#### Relational Tension
- `closeness_vs_threshold`
- `devotion_vs_distance`
- `warmth_vs_self_protection`

#### Action Tension
- `speed_vs_control`
- `impulse_vs_method`
- `expansion_vs_caution`

#### Visibility Tension
- `public_refinement_vs_visibility_sensitivity`
- `recognition_drive_vs_backstage_creation`

#### Regulation Tension
- `mental_precision_vs_flow`
- `inner_critic_vs_creative_expression`

### V1 Priority Contradictions
Implement these first:
- `visibility_vs_private_preparation`
- `closeness_vs_threshold`
- `structure_vs_originality`
- `composure_vs_internal_pressure`
- `speed_vs_control`

### Contradiction Use Rules
- No contradiction should exist without evidence from both sides.
- High-score contradictions should increase profile specificity.
- Contradictions should not replace the primary spine unless they are identity-defining.

## 9. Line Selection Rules

### Global Rules
- Do not let all lines come from the same planet cluster.
- Do not let all lines come from the same house arena.
- At least one of the top two lines must reference top identity/regulation primitives.
- If relational line outranks primary identity line globally, do not swap slots; keep role semantics stable.

### Selection Sequence
1. select `primary_identity_spine`
2. remove conflicting clones
3. select `secondary_balancing_line`
4. select `relational_line`
5. select `work_visibility_line`
6. select `shadow_protection_line`

### Clone Rule
Two candidates are clones if:
- overlap in primitive set >= 0.67
- semantic family equal
- same dominant planet cluster

When cloned:
- keep higher confidence candidate
- demote other to support

## 10. Layer Arbitration Rules

Add or evolve:
- `backend/app/natal/narrative/layer_arbitrator.py`

Target output:

```python
{
    "engine_version": "layer_arbitrator_v1",
    "scores": {
        "core_story": 0.88,
        "profile_narrative": 0.79,
        "personality_imprint": 0.69,
        "sections_v2": 0.74,
        "supporting_threads": 0.72,
    },
    "rejected_or_demoted_blocks": [],
}
```

### Alignment Scoring

Each layer block should get:

```python
alignment =
    spine_alignment * 0.45
    + slot_alignment * 0.20
    + contradiction_alignment * 0.15
    + semantic_novelty * 0.10
    + evidence_coverage * 0.10
```

### Arbitration Outcomes
- `keep`
- `rewrite`
- `demote_to_support`
- `drop`

### Surface Rules

#### Core Story
- Must align mostly with `primary_identity_spine`
- Can mention `secondary_balancing_line`
- Should not be led by shadow line

#### Profile Narrative
- Must align with primary plus secondary
- Relational/work/shadow can be separate blocks
- Contradictions should be explicit if they are high-score

#### Personality Imprint
- May surface strong combinations
- Must not create a rival personality thesis

#### Sections V2
- Support-only by default
- If too close to core story, compress or demote

#### Supporting Threads
- Should elaborate side layers, not replace the center

## 11. Rewrite Policy

For Phase 4/5 arbitration, rewrite should remain deterministic.

Allowed rewrite actions:
- replace headline
- replace teaser
- shorten body
- reclassify from primary card to support card
- remove chip set

Not allowed:
- free-generate new meaning outside selected evidence

## 12. Rollout Feature Flag Plan

Config home:
- `backend/app/config/natal/natal_selection_v3.yaml`

### Phase 1
- `feature_foundation_debug: true`
- everything else `false`

### Phase 2
- `master_selector_enabled: true`
- use only in debug

### Phase 3
- `contradiction_engine_enabled: true`
- use in debug and selector scoring

### Phase 4
- `layer_arbitration_enabled: true`
- debug only first

### Phase 5
- `surface_migration_enabled: true`
- gated rollout

### Phase 6
- `voice_profile_enabled: true`

### Recommended Additional Flags
- `selector_debug_only`
- `selector_shadow_compare`
- `profile_narrative_selector_rollout_pct`
- `personality_imprint_selector_rollout_pct`
- `supporting_threads_selector_rollout_pct`
- `voice_profile_rollout_pct`

## 13. Debug Payload Requirements

When debug is on, selector should emit:
- `selected_identity_spine`
- `selected_secondary_line`
- `selected_relational_line`
- `selected_work_visibility_line`
- `selected_shadow_protection_line`
- `selector_candidate_pool`
- `selector_score_breakdown`
- `contradiction_signatures`
- `cross_layer_consistency_scores`
- `rejected_or_demoted_blocks`
- `old_vs_new_selection_diff`

## 14. Implementation Sequence

### Immediate Next Build
1. implement real candidate generation in `master_selector.py`
2. implement v1 contradiction taxonomy in `contradiction_engine.py`
3. wire both into route debug
4. implement alignment scoring in `layer_arbitrator.py`

### Then
5. migrate `profile_narrative`
6. migrate `personality_imprint`
7. migrate `supporting_threads`
8. add voice profile

## 15. Success Definition

The new system is working when:
- one clear primary identity spine is always visible
- secondary line adds nuance instead of conflict
- contradictions feel central, not decorative
- profile surfaces stop sounding like separate subsystems
- debug output makes the selection explainable end-to-end
