# Adaptive Period Cards Phase 1 Readiness Audit

## TL;DR

- The best primary insertion point for Phase 1 context contracts is `backend/app/transit/narrative/deep_archetype_engine.py::build_period_core(...)`.
- That is the only current layer that naturally sees:
  - selected/evidence-bearing `featured_events`
  - `semantic_focus_result`
  - `chapter_priority`
  - `canonical_period_spine`
  - `active_life_chapter`
  - `canonical_natal_state`
  - final renderer output including `period_reading_v1` and `composer_plan`
- `astrolog_narrative_engine.py::build_period_story(...)` is too renderer-specific and does not cleanly own canonical natal inputs.
- `public_builder.py::build_public_response(...)` is too late in the pipeline and would force Phase 1 contracts to be built from normalized public copy instead of semantic/evidence structures.
- `transits.py` route layer has canonical natal state and route wiring, but it is the wrong primary owner because it would duplicate semantic assembly logic and split behavior across full/home/public paths.
- The biggest nuance is `period_core.natal_activation_context`: it exists in final route payloads, but it is injected later in `transits.py`, not inside `build_period_core(...)`. For Phase 1 it should be treated as optional enrichment, not a required primary input.
- Current codebase has no truly hidden internal `period_core` slot. Underscore-prefixed fields still pass through `public_builder`. If Phase 1 emits contexts, it needs either:
  - a real debug/internal gate, or
  - artifact/test-only placement first.

## 1. Final Recommendation

### Chosen insertion point

`backend/app/transit/narrative/deep_archetype_engine.py::build_period_core(...)`

### Why

It is the narrowest layer where period semantic ownership, evidence selection, chapter routing, canonical period spine, canonical natal state, and final period prose all meet before route/public reshaping.

### Phase 1 recommendation

Implement Phase 1 as:

1. `build_period_core(...)` computes `PeriodCardContext`
2. the same layer computes a minimal `NatalContextForPeriodCards` projection from canonical natal state plus period-linked evidence
3. both contracts remain internal/debug-oriented
4. no public card copy yet
5. no `period_signal_lines_v1` yet

### Important nuance

Do not make `period_core.natal_activation_context` mandatory in v1 contract assembly. It is not present yet at the natural insertion point. Use:

- `canonical_period_spine`
- `canonical_natal_state`
- `featured_events[].derived_context`
- `active_life_chapter.renderer_handoff`

as the stable Phase 1 base, and treat `natal_activation_context` as optional later enrichment.

## 2. Current Runtime Chain

The real runtime path today is:

`transits.py`
→ `_attach_internal_period_reasoning_state(...)`
→ `build_public_response(...)`
→ `build_period_core(...)`
→ `resolve_period_semantic_focus(...)`
→ `chapter_priority`
→ `build_period_story(...)`
→ `composer_plan`
→ `period_reading_v1`
→ route-level `natal_activation_context` injection
→ final public payload

### Important actual ownership split

- `transits.py` attaches:
  - `_canonical_natal_state`
  - `_active_life_chapter`
- `public_builder.py` builds:
  - `canonical_period_spine`
  - `period_core`
- `deep_archetype_engine.py` builds:
  - `featured_events`
  - `semantic_focus`
  - `chapter_priority`
  - `period_reading_v1`
  - `_period_story_debug`
- `transits.py` later injects:
  - `period_core.natal_activation_context`

That split matters for Phase 1 contract design.

## 3. Best Insertion Point Comparison

### Option A — `deep_archetype_engine.py::build_period_core(...)`

#### Available inputs

- selected event cards
- enriched `featured_events`
- `canonical_period_spine`
- `active_life_chapter`
- `canonical_natal_state`
- `semantic_focus_result`
- `chapter_priority`
- final `period_reading_v1`
- final `composer_plan` via `_period_story_debug`

#### Pros

- closest to current semantic owner chain
- has both evidence and final renderer framing
- avoids building context from normalized public text
- avoids duplicating route logic
- easiest place to keep cards downstream of `semantic_focus_result`

#### Cons

- `period_core.natal_activation_context` is not yet injected here
- home-lite path is separate
- output from this layer is still later normalized by `public_builder`

#### Risk

Medium-low. Best structural fit if the contract stays minimal and does not require later-injected fields.

#### Decision

Chosen.

### Option B — `astrolog_narrative_engine.py::build_period_story(...)`

#### Available inputs

- `period_core`
- `semantic_focus_result`
- `active_life_chapter`
- `canonical_period_spine`
- `period_voice_policy`
- `composer_plan`
- `period_reading_v1`

#### Pros

- has the strongest final framing data
- direct access to `composer_plan`
- direct access to `period_voice_policy.manifestation_context`

#### Cons

- renderer-specific ownership
- wrong place to build evidence contract from canonical natal structure
- no clean first-class `canonical_natal_state` contract here
- would mix context projection with prose renderer responsibilities

#### Risk

Medium-high. Too likely to turn the card context into a renderer-adjacent surface instead of a semantic/evidence contract.

#### Decision

Do not choose as the primary owner.

### Option C — `public_builder.py::build_public_response(...)`

#### Available inputs

- `response`
- `_canonical_natal_state`
- `_active_life_chapter`
- `canonical_period_spine`
- finished `period_core`

#### Pros

- sees the already-assembled public `period_core`
- can access canonical natal state from route response
- shared full/home payload shaping logic exists here

#### Cons

- too late in the pipeline
- would build internal semantic context from normalized public payload
- EN rewrite and normalization have already touched copy
- duplicates or re-reads semantic structures instead of owning them upstream

#### Risk

Medium. Safer than route layer, but still not the natural owner.

#### Decision

Not chosen as primary insertion point.

### Option D — `transits.py` route layer

#### Available inputs

- raw core response
- `_canonical_natal_state`
- `_active_life_chapter`
- final public payload
- route-only injections like `natal_activation_context`

#### Pros

- can see route-specific enrichments
- has the already-injected `natal_activation_context`

#### Cons

- too late and too broad
- duplicates ownership logic across route modes
- risks divergence between full payload, home payload, and public-only payload
- wrong layer to decide semantic/evidence contract

#### Risk

High.

#### Decision

Do not choose as primary owner.

## 4. Period Inputs Availability

Status labels:

- `available`: usable at chosen insertion point
- `partial`: exists only later, or only via debug/local variable, or unstable across full/home
- `missing`: not reliably available in a way suitable for Phase 1

| Input | Status | Exact path at runtime | Producer | Shape | Stability | Notes |
|---|---|---|---|---|---|---|
| `period_core.semantic_focus` | available | `result["semantic_focus"]` in `build_period_core(...)` | `resolve_period_semantic_focus(...)` | debug dict | High | Strong owner input |
| `period_core.chapter_priority` | available | `result["chapter_priority"]` | `_build_chapter_priority_debug(...)` | dict | High | Strong routing input |
| `period_core.canonical_period_spine` | available | `result["canonical_period_spine"]` | `build_canonical_period_spine(...)` via `public_builder` | dict | High | Strong period→natal bridge |
| `period_core.natal_activation_context` | partial | injected later by `transits.py::_inject_canonical_natal_activation_context(...)` | `build_transit_natal_activation_context(...)` | dict | Medium | Not present yet in `build_period_core(...)` |
| `period_core.featured_events[]` | available | `result["featured_events"]` | `build_period_core(...)` | list[dict] | High | Main evidence pool |
| `featured_events[].derived_context` | available | merged into `selected_enriched` | hybrid context in `deep_archetype_engine.py` | dict | High | Strong evidence support |
| `featured_events[].chapter_role` | available | merged from selected event cards | selection pipeline | dict | Medium-high | Good routing/ranking hint |
| `featured_events[].story_score` | available | merged from selected event cards | selection pipeline | float | Medium-high | Ranking only, not authority |
| `featured_events[].timing` | available | event card payload | event/public pipeline | dict | Medium | Good timing hint |
| `featured_events[].phase` | available | event card payload | event/public pipeline | str | Medium-high | Good timing hint |
| `featured_events[].bucket` | available | event card payload | event/public pipeline | str | Medium-high | Good timing hint |
| `manifestation_context` | partial | local `policy_seed["manifestation_context"]`; also mirrored in `_period_story_debug["period_voice_policy_manifestation_context"]` | `build_period_voice_policy(...)` | dict | Medium-high | Available locally, not first-class period_core field |
| `suppressed_meanings` | available | `semantic_focus["suppressed_meanings"]`; also `_period_story_debug["suppressed_meanings_applied"]` | semantic focus + guided renderer | list[str] | High | Mandatory guardrail input |
| `period_reading_v1` | available | `result["period_reading_v1"]` | `build_period_story(...)` | dict | High | Framing/proof only |
| `composer_plan` | available | `result["_period_story_debug"]["composer_plan"]` | `build_period_story(...)` | dict | High | Framing-only |

### Key period-side conclusion

The Phase 1 `PeriodCardContext` can be built safely today from:

- `semantic_focus`
- `chapter_priority`
- `canonical_period_spine`
- `featured_events`
- `manifestation_context` from local policy seed
- `period_reading_v1`
- `composer_plan`

It should not require `natal_activation_context` as a mandatory field in v1.

## 5. Natal Inputs Availability

| Input | Status | Where available | Safe for Phase 1? | Notes |
|---|---|---|---|---|
| `_canonical_natal_state` | available | route response before `build_public_response(...)`; passed into `build_period_core(...)` as `canonical_natal_state` | Yes | Canonical upstream source |
| `CanonicalNatalStateV1.core_promises` | available | canonical state object | Yes | Strong canonical source |
| `CanonicalNatalStateV1.contradictions` | available | canonical state object | Yes | Strong canonical source |
| `CanonicalNatalStateV1.chart_spine` | available | canonical state object | Yes | Strong canonical source |
| `meaning_graph.activation_hooks` | available | `canonical_state.meaning_graph["activation_hooks"]` | Yes | Already used by activation pipeline |
| `structural_state.dispositor_routes` | available | canonical state object | Yes, carefully | Raw shape needs projection/normalization |
| `structural_state.house_ruler_routes` | available | canonical state object | Yes, carefully | Raw shape needs projection/normalization |
| `canonical_natal_activation` outputs | partial | `canonical_period_spine` available early; `natal_activation_context` only route-injected later | Yes | Treat `canonical_period_spine` as stable, `natal_activation_context` as optional |
| event `derived_context` | available | `featured_events[].derived_context` | Yes | Strong event-linked natal bridge |
| event `natal_promise` | partial | often present on event cards, not guaranteed as stable minimal runtime contract | Yes, optional | Good when present, not mandatory |
| `active_life_chapter.renderer_handoff` | available | `active_life_chapter` mapping | Yes | Strong Tier-1 framing bridge |
| `active_life_chapter.natal_architecture_anchor` | available | `active_life_chapter` mapping | Yes | Strong Tier-1 personalization bridge |

### Natal-side conclusion

At the chosen insertion point, canonical natal authority is available, but in a raw object-heavy form.

That means `NatalContextForPeriodCards` should be:

- a projection layer
- small
- ID/reference-first
- normalized from canonical state

It should not copy broad rendered natal text into the contract.

## 6. Blocked Source Check

These sources are confirmed as the wrong authority for Phase 1 and should remain blocked:

| Source | Why blocked |
|---|---|
| old top-level `blocks[]` | legacy assembler/UI surface, not the semantic period pipeline |
| `daily_synthesis.body` | daily-owned copy, not period-owner authority |
| `best_times.score_by_intent` | timing score, not meaning |
| raw `heat` / `rating` | calendar intensity only |
| `profile_v8` | rendered profile surface, not canonical natal authority |
| `full_map_v8` | rendered profile/natal surface |
| `personality_imprint` | editorial identity layer, too broad for period-authority use |
| `meaning_graph_v1_1` | downstream/public-facing graph surface, not canonical period input |
| projection outputs | rendered/projection surfaces, not semantic source |
| `story_tracks` as owner | legacy grouping/render-support only |
| `_event_story_map` as owner | legacy event→track mapping only |

## 7. Proposed Minimal Phase 1 Contract Shapes

The v1 contract should be smaller than the architecture-plan idealized shape. Only reliably available fields should be required.

### `PeriodCardContext`

```python
PeriodCardContext = {
    "version": "period_card_context_v1",
    "owner_ref": {
        "source": str,
        "selected_meaning": str,
        "meaning_family": str | None,
        "confidence": float,
    },
    "chapter_priority": {
        "applied": bool,
        "owner": str | None,
        "chapter_type": str | None,
        "event_cards_role": str | None,
    },
    "primary_domain": str | None,
    "secondary_domains": list[str],
    "suppressed_meanings": list[str],
    "canonical_period_spine_ref": {
        "hook_id": str | None,
        "target_node_id": str | None,
        "primary_domain": str | None,
        "spine_lines": list[str],
    },
    "period_reading_ref": {
        "version": str | None,
        "full_text": str | None,
        "block_roles": list[str],
    },
    "composer_frame": {
        "semantic_mode": str | None,
        "hook": str | None,
        "scene_anchor": str | None,
        "core_contrast": str | None,
        "mechanism": str | None,
        "growth_edge": str | None,
        "what_it_builds": str | None,
        "closer": str | None,
    },
    "manifestation_context": dict | None,
    "natal_activation_ref": {
        "matched_event_ids": list[str],
        "top_hook_ids": list[str],
    } | None,
    "evidence_items": list["PeriodEvidenceItem"],
    "debug": dict,
}
```

### `PeriodEvidenceItem`

```python
PeriodEvidenceItem = {
    "event_id": str,
    "rank": int,
    "evidence_role": str | None,
    "transit_body": str | None,
    "natal_point": str | None,
    "aspect": str | None,
    "phase": str | None,
    "bucket": str | None,
    "chapter_role": dict | None,
    "story_score": float | None,
    "semantic_owner": str | None,
    "derived_context": {
        "natal_target": dict | None,
        "connected_points": list[dict],
        "motifs": list[str],
        "derived_domains": list[str],
    } | None,
    "natal_promise": dict | None,
    "timing": dict | None,
    "debug_refs": dict,
}
```

### `NatalContextForPeriodCards`

```python
NatalContextForPeriodCards = {
    "version": "natal_context_for_period_cards_v1",
    "chart_id": str | None,
    "semantic_owner_ref": {
        "source": str,
        "selected_meaning": str,
    },
    "activated_core_promise_ids": list[str],
    "activated_contradiction_ids": list[str],
    "chart_spine_refs": list[dict],
    "activation_hook_refs": list[dict],
    "dispositor_route_refs": list[dict],
    "house_ruler_route_refs": list[dict],
    "event_natal_links": list[dict],
    "life_chapter_bridge": {
        "renderer_handoff": dict | None,
        "natal_architecture_anchor": dict | None,
    },
    "suppressed_identity_claims": list[str],
    "debug": dict,
}
```

### `CardCandidateContext`

Recommendation for Phase 1:

- define conceptually
- do not emit yet

If needed for test scaffolding, keep it private and optional. Do not make it part of the Phase 1 payload contract.

## 8. Phase 1 Output Placement

### Safest recommendation

Internal/debug-only placement.

### Reality check

Current codebase does **not** have a truly hidden `period_core` internal slot:

- `public_builder._normalize_period_core_copy(...)` does not drop unknown underscore fields
- `build_public_response(..., include_debug_artifacts=False)` still passes underscore `period_core` fields through

### Recommended placement options

#### Best if runtime gating is added in the future

`period_core["_adaptive_cards_context"] = { ... }`

with nested:

- `_period_card_context`
- `_natal_context_for_period_cards`

#### Safest without adding a new public/debug gate yet

Artifact/test-only first.

That means:

- build the projection in code later
- validate it in tests/artifacts
- do not expose it publicly until a real internal/debug gate exists

### Final placement recommendation

For the implementation PR, prefer:

1. internal underscore placement under `period_core["_adaptive_cards_context"]`
2. but only if the PR also ensures that internal context does not leak to normal public/mobile consumers

If that gate is not part of the PR, then Phase 1 should stay artifact-only rather than shipping a pseudo-internal public field.

## 9. Tests Needed Before Code Work

### New suggested test file

`backend/tests/test_adaptive_period_cards_context_contract.py`

### Contract tests

1. context exists when period evidence exists
2. `PeriodCardContext.owner_ref` matches `semantic_focus`
3. `PeriodCardContext.evidence_items` link back to `featured_events`
4. `composer_frame` comes from `composer_plan`, not reparsed prose
5. `period_reading_ref` is framing-only and does not become owner
6. blocked sources are absent:
   - old `blocks[]`
   - `daily_synthesis.body`
   - `best_times.score_by_intent`
   - `story_tracks` as owner
   - `_event_story_map` as owner
7. chapter-priority cases orbit chapter owner
8. non-LifeChapter cases remain evidence-guided
9. `period_reading_v1` remains unchanged
10. daily remains unchanged
11. natal remains unchanged
12. PR-D remains unchanged

### Route-shaped / real-case tests

Use:

- `2026-03-04` Istanbul real route case
- `2026-04-22` Istanbul real route case
- Cancer 8th Saturn return fixture
- Nodal Aries/Libra fixture

Suggested assertions:

- `2026-03-04`
  - context exists
  - owner is still the current semantic owner
  - chapter-aware refs exist if active chapter exists
- `2026-04-22`
  - context exists
  - no faux LifeChapter owner
  - evidence items still present
- Cancer 8th Saturn return
  - context suppression list matches chapter suppression
  - `renderer_handoff` bridge survives into natal context
- Nodal Aries/Libra
  - `chapter_priority.applied == true` still orbits directional self-definition

### Existing tests likely to update

- `backend/tests/test_transit_narrative_public_payload.py`
- `backend/tests/test_period_semantic_focus.py`
- `backend/tests/test_period_reading_v1_contract.py`
- `backend/tests/test_pr_d_v1_flag.py`

## 10. Risk Assessment

### 1. Context contract becoming too large

Risk:

- Phase 1 quietly becomes pre-rendered card planning instead of a narrow context contract

Mitigation:

- ID/reference-first shape
- optional fields stay optional
- no prose fields beyond framing refs

### 2. Debug/internal fields leaking into public UI

Risk:

- underscore placement is not enough today

Mitigation:

- add explicit debug/internal gating before public exposure
- otherwise keep Phase 1 artifact-only

### 3. Accidentally using rendered profile surfaces as authority

Risk:

- `profile_v8`, `personality_imprint`, `meaning_graph_v1_1`, projection outputs re-enter as hidden owner

Mitigation:

- explicit blocked-source tests

### 4. Duplicating semantic-focus logic

Risk:

- card context recomputes meaning instead of organizing evidence

Mitigation:

- `owner_ref` must point to existing `semantic_focus`
- no new meaning-selection step in Phase 1

### 5. Adding card-like copy too early

Risk:

- Phase 1 starts shipping prose before contracts are stable

Mitigation:

- no public card copy
- no `period_signal_lines_v1` prose yet

### 6. Snapshot/test blast radius

Risk:

- additive internal payload fields affect snapshots broadly

Mitigation:

- keep Phase 1 minimal
- prefer dedicated contract tests over broad snapshot churn

## 11. Recommended PR Order

1. Phase 1 context contracts only
2. Dedicated adaptive cards voice reference doc
3. Backend additive `period_signal_lines_v1` rendering
4. Mobile expandable UI
5. Old `blocks[]` deprecation

### Adjustment from code findings

Do **not** start with public card rendering.

The codebase is ready for:

- context assembly
- evidence tracing
- semantic-owner-preserving projection

It is **not** ready to safely expose internal card contexts publicly without a clearer debug/internal gate.

## 12. Next PR Prompt Skeleton

```text
Implement Adaptive Period Cards Phase 1 context contracts only.

Do not generate public card copy.
Do not add period_signal_lines_v1 prose yet.
Do not change mobile.
Do not change event selection.
Do not change daily/natal/PR-D behavior.

Primary insertion point:
backend/app/transit/narrative/deep_archetype_engine.py::build_period_core(...)

Goal:
Emit narrow internal context contracts for future adaptive period cards:
- PeriodCardContext / PeriodEvidenceItem
- NatalContextForPeriodCards

Required rules:
- semantic_focus remains owner
- chapter_priority remains routing gate
- composer_plan and period_reading_v1 are framing-only
- blocked sources must not be used
- no second meaning engine

Input rules:
- require semantic_focus, chapter_priority, canonical_period_spine, featured_events, derived_context, composer_plan, period_reading_v1
- treat natal_activation_context as optional enrichment, not mandatory
- use canonical_natal_state directly for natal projection

Placement:
- internal/debug-oriented only
- do not expose as public card copy
- if no true internal gate exists, keep Phase 1 artifact-only or underscore-prefixed with explicit tests

Tests:
- add test_adaptive_period_cards_context_contract.py
- use 2026-03-04 Istanbul
- use 2026-04-22 Istanbul
- use Cancer 8th Saturn return fixture
- use Nodal Aries/Libra fixture
- assert period_reading_v1 unchanged
- assert no blocked sources
- assert owner/evidence traceability
```

## 13. Bottom Line

Phase 1 is ready, but only if the implementation stays narrow.

The codebase already has enough period and natal computation to emit context contracts safely. The correct move is not to invent card meaning, and not to build from public copy. The correct move is:

- build in `build_period_core(...)`
- keep `semantic_focus` as owner
- keep renderer outputs as framing only
- project canonical natal structure narrowly
- avoid public card copy until the context contracts are validated
