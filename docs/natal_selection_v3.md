# Natal Selection V3

Updated: 2026-04-02

## Goal
- Keep the current natal computation and rule infrastructure.
- Add one central selection layer so `core_story`, `profile_narrative`, `personality_imprint`, `sections_v2`, and `supporting_threads` derive from the same personality spine.
- Move the system from "many parallel interpretation surfaces" to "one shared spine with multiple renderers".

## Current Constraint
- The current route builds `natal_graph`, composite/pattern engines, `expression_profile`, `core_story`, `sections_v2`, `supporting_threads`, `profile_narrative`, and `personality_imprint` sequentially, but these outputs do not share a common selector contract.
- `natal_graph.importance` is still mostly angular house + angle ruler + aspect count.
- `primitive_engine` produces useful human-centered abstractions, but it is not the top-level arbitration layer.
- `personality_imprint` still ranks mostly by library match plus simple importance tie-break.
- `expression_resolver` uses broad pressure/support state instead of a personality-derived voice profile.

## Design Principle
- Do not replace the current engines.
- Insert one new deterministic layer in the middle.
- Make all public surfaces consume the same selection payload.

Target pipeline:

`astro signals -> natal feature graph -> primitives -> identity spine -> layer arbitration -> editorial rendering`

## Proposed Architecture

### 1. Natal Feature Graph V3
Add a new file:
- `backend/app/natal/natal_feature_graph.py`

Responsibility:
- Build one normalized feature payload for all downstream selectors.
- Reuse existing `natal_graph` and `natal_graph_v2` pieces instead of duplicating signal extraction.

Suggested output shape:

```python
{
    "planet_salience": {
        "Sun": {
            "score": 0.81,
            "components": {
                "angularity": 0.18,
                "chart_ruler_weight": 0.12,
                "luminary_weight": 0.16,
                "aspect_density": 0.08,
                "aspect_exactness": 0.07,
                "dispositor_centrality": 0.09,
                "motif_density": 0.06,
                "contradiction_load": 0.05,
            },
        },
    },
    "motifs": [],
    "polarities": [],
    "house_ruler_routes": {},
    "public_private_split": {},
    "voice_inputs": {},
}
```

New score families:
- `chart_ruler_centrality`
- `luminary_condition`
- `angular_dominance`
- `house_ruler_recursion`
- `dispositor_centrality`
- `exact_aspect_salience`
- `repeated_motif_density`
- `contradiction_load`
- `compensation_signal`
- `public_private_split`

Implementation note:
- Keep `backend/app/natal/natal_graph.py` as compatibility output.
- Build V3 from:
  - `backend/app/natal/natal_graph.py`
  - `backend/app/natal/natal_graph_v2.py`
  - existing aspects, house rulers, dispositor chains, motifs

### 2. Primitive Engine V2
Keep:
- `backend/app/natal/narrative/primitive_engine.py`

Add:
- `backend/app/natal/narrative/primitive_engine_v2.py`

Responsibility:
- Convert feature graph outputs into scored human primitives.
- Separate primitive types clearly:
  - `identity`
  - `regulation`
  - `relational`
  - `visibility`
  - `shadow`
  - `compensation`

Suggested primitive payload:

```python
{
    "primitive_id": "inner_structure",
    "score": 0.74,
    "confidence": 0.79,
    "salience": 0.83,
    "polarity": "stabilizing",
    "evidence": [],
    "counterweights": ["originality_drive"],
    "source_features": ["saturn_angular", "mercury_saturn_link"],
}
```

New rules:
- Primitive scores should use feature components, not only direct placements/aspects.
- A primitive can be boosted or softened by contradiction/counterweight pairs.
- Primitive output should expose:
  - `top_primitives`
  - `shadow_primitives`
  - `compensation_primitives`
  - `relational_primitives`
  - `visibility_primitives`

### 3. Master Natal Selector
Add:
- `backend/app/natal/selection/master_selector.py`
- `backend/app/natal/selection/contracts.py`

This becomes the main arbitration layer.

Suggested output shape:

```python
{
    "engine_version": "natal_selection_v3",
    "identity_spine": {
        "primary_line": {},
        "secondary_line": {},
        "relational_line": {},
        "work_visibility_line": {},
        "shadow_protection_line": {},
    },
    "signature_contradictions": [],
    "voice_profile": {},
    "layer_guidance": {
        "core_story": {},
        "profile_narrative": {},
        "personality_imprint": {},
        "sections_v2": {},
        "supporting_threads": {},
    },
    "consistency": {},
}
```

Selection responsibilities:
- Pick the top 1 `primary_line` that defines the chart's center.
- Pick 1 `secondary_line` that balances or modifies the center.
- Pick 1 `relational_line`.
- Pick 1 `work_visibility_line`.
- Pick 1 `shadow_protection_line`.
- Pick 2 contradiction pairs.
- Produce a deterministic `voice_profile`.

Scoring logic:
- `final_line_score = primitive_strength + feature_support + motif_support + contradiction_bonus - redundancy_penalty - incoherence_penalty`

Selection constraints:
- At least one line must come from top identity/regulation primitives.
- Lines cannot all be sourced from the same house or same planet cluster.
- If two lines strongly overlap semantically, collapse one into support.
- If a line conflicts with the selected primary spine without explicit contradiction framing, demote it.

### 4. Contradiction Engine
Add:
- `backend/app/natal/selection/contradiction_engine.py`

Responsibility:
- Detect "both are true" pairs that make the profile feel personally accurate.

Examples:
- `visible_presence` + `backstage_creation`
- `originality_drive` + `inner_structure`
- `intimacy_depth` + `emotional_threshold`
- `push_pull_drive` + `methodical_drive`

Suggested output:

```python
{
    "id": "visibility_vs_inward_preparation",
    "left": "visible_presence",
    "right": "backstage_creation",
    "score": 0.72,
    "type": "tension",
    "editorial_pattern": "You want visibility, but only after internal preparation feels real."
}
```

Rules:
- Contradictions should be explicit system objects, not incidental prose.
- They should feed `profile_narrative`, `supporting_threads`, and `personality_imprint`.
- At least one contradiction should appear in the public profile when confidence is high enough.

### 5. Voice Profile V2
Add:
- `backend/app/resolvers/voice_profile_resolver.py`

Keep:
- `backend/app/resolvers/expression_resolver.py`

Change:
- `expression_resolver` should stop acting as the main personality tone selector.
- It should become a fallback render policy resolver that consumes `voice_profile`.

Suggested voice dimensions:
- `directness`: direct vs reflective
- `warmth`: warm vs restrained
- `texture`: poetic vs crisp
- `playfulness`: playful vs serious
- `holding_style`: confrontive vs containing
- `sentence_motion`: clipped vs flowing

Voice inputs:
- pressure/support state
- identity spine
- contradiction type
- dominant primitive family
- public/private split

### 6. Cross-Layer Arbitration
Add:
- `backend/app/natal/selection/layer_arbitrator.py`

Responsibility:
- Validate whether each surface aligns with the selected spine.
- Downrank or rewrite surfaces that drift.

Suggested output:

```python
{
    "core_story": {"alignment": 0.88, "action": "keep"},
    "profile_narrative": {"alignment": 0.79, "action": "rewrite_teaser"},
    "personality_imprint": {"alignment": 0.63, "action": "demote_bundle"},
    "sections_v2": {"alignment": 0.71, "action": "support_only"},
}
```

Rules:
- `core_story` must stay closest to `primary_line`.
- `profile_narrative` can carry more nuance but must still anchor to the same spine.
- `personality_imprint` can surface combinations, but not contradict the spine without contradiction framing.
- `sections_v2` and `supporting_threads` are support surfaces, not competing narratives.

## Integration Plan

### Route Integration
Update:
- `backend/app/api/routes/natal_interpretation.py`

Current order:
- compute graph
- build composites/patterns
- build expression profile
- build core story
- build sections/supporting/profile/imprint

Proposed order:
- compute `natal_graph`
- compute `natal_feature_graph`
- compute `primitive_engine_v2`
- compute `master_selector`
- compute `voice_profile`
- pass selector payload into:
  - `JoviaSemanticNarrativeBuilder`
  - `build_profile_narrative`
  - `build_personality_imprint`
  - `build_sections_v2`
  - `build_supporting_threads`
- run `layer_arbitrator`
- build public payload

### Existing Files To Keep
- `backend/app/natal/natal_graph.py`
- `backend/app/natal/natal_graph_v2.py`
- `backend/app/natal/narrative/primitive_engine.py`
- `backend/app/natal/narrative/signature_engine.py`
- `backend/app/natal/personality_imprint/selector.py`
- `backend/app/natal/public_builder.py`

### Existing Files To Change
- `backend/app/api/routes/natal_interpretation.py`
- `backend/app/resolvers/expression_resolver.py`
- `backend/app/natal/narrative/profile_narrative_engine.py`
- `backend/app/natal/narrative/profile_narrative_engine_signature.py`
- `backend/app/natal/personality_imprint/builder.py`
- `backend/app/natal/personality_imprint/selector.py`
- `backend/app/natal/supporting_threads_builder.py`
- `backend/app/natal/public_builder.py`

## Surface-Specific Adaptation

### Core Story
- Consume `identity_spine.primary_line` and `secondary_line`.
- Use contradictions only as second paragraph material.
- Never let support layers redefine the main thesis.

### Profile Narrative
- Use `primary_line`, `secondary_line`, `relational_line`, `work_visibility_line`.
- Signature block selection should become selector-guided instead of catalog-first.
- Existing signature catalog remains useful as rendering inventory, not as final arbitration authority.

### Personality Imprint
- Move from `placement/aspect -> library match` toward:
  - `selector line -> bundle family -> library entry`
- Library entries remain, but ranking should include:
  - primitive support
  - contradiction relevance
  - lived salience
  - cross-line consistency

### Sections V2 / Supporting Threads
- Generate only from non-primary lines or contradiction/support layers.
- If a thread duplicates the main spine, suppress it.

### Public Builder
- Expose new public hierarchy:
  - `identity_spine.headline`
  - `signature_cards`
  - `contradictions`
  - `supporting_detail`

## Rollout

### Phase 1: Observe Only
- Add feature graph and selector in debug mode only.
- Keep current output unchanged.
- Log:
  - top primitives
  - selected spine
  - contradictions
  - layer alignment scores

### Phase 2: Shadow Routing
- Feed selector payload into `profile_narrative` debug output.
- Compare:
  - current selected blocks
  - selector-guided blocks
- Do not change public payload yet.

### Phase 3: Profile Narrative First
- Switch `profile_narrative` to selector-guided mode.
- Leave `personality_imprint`, `sections_v2`, `supporting_threads` on legacy ranking.

### Phase 4: Personality Imprint + Supporting Layers
- Migrate `personality_imprint`.
- Then migrate `sections_v2` and `supporting_threads`.

### Phase 5: Voice + Arbitration
- Turn on `voice_profile_resolver`.
- Turn on cross-layer arbitration.
- Add public hierarchy cleanup.

## Success Metrics
- Higher agreement between `core_story`, `profile_narrative`, and `personality_imprint`.
- Fewer contradictory top-level impressions on the profile screen.
- More repeatable "this profile sees me" feedback due to contradiction framing.
- Lower semantic duplication across cards and sections.

## Immediate Highest-Value Build Order
1. `natal_feature_graph.py`
2. `primitive_engine_v2.py`
3. `master_selector.py`
4. `contradiction_engine.py`
5. route wiring in `natal_interpretation.py`
6. selector-guided `profile_narrative`
7. selector-guided `personality_imprint`
8. `voice_profile_resolver.py`
9. `layer_arbitrator.py`

## Non-Goals
- Replacing the natal math engine
- Making the system LLM-first
- Removing existing catalogs or phrase libraries
- Rebuilding mobile UI before selector convergence is achieved
