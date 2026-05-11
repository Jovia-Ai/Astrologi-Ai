# PR-D v1 Readiness After PR-SF1 and PR-4.1

Generated on 2026-05-05.

## Executive Decision

**Decision: `go behind flag only`**

Broad/global PR-D is still too wide. A **scoped PR-D v1** is now implementable **behind a feature flag** because the critical prerequisites are in place:

- `active_life_chapter` now exists in the live runtime transit path.
- `PeriodSemanticFocusResolver` can already select `source="life_chapter"` for high-confidence Tier-1 chapters.
- `astrolog_narrative_engine.py` now consumes that semantic ownership and produces chapter-owned prose for the Tier-1 proof cases.
- Fallback behavior without a chapter still works.
- Public payload changes remain additive.

The remaining risks are real but bounded:

- event selection is still materially event-first
- daily is still not chapter-aware
- extraction tooling still partially bypasses the runtime path
- Cancer 8th and nodal prose are correct but still polishable

That combination supports **PR-D v1 behind flag**, but not an always-on rollout.

## 1. PR-D v1 Scope

### Allowed in PR-D v1

- `saturn_return`
- `nodal_return`
- `nodal_activation`

### Explicitly excluded from PR-D v1

- `structural_natal_chapter`
- `profection_year`
- `progressed_lunation`
- `solar_return_theme` as owner
- `outer_planet_angle_hit`
- best-times / opportunity ownership
- daily chapter ownership

### Evidence for exclusion

- `backend/app/transit/narrative/life_chapter_detector.py`
  - structural candidate debug explicitly sets:
    - `readiness_status = "not_ready"`
    - `excluded_from_pr_d_v1 = True`
    - `future_candidate_pr = "PR-C.4"`
- `docs/system/life_chapter_signal_registry.md`
  - structural natal pattern is still documented as `partial`, `debug_only`, and excluded from PR-D v1.

## 2. Current Prerequisites

| Prerequisite | Status | Evidence | Notes |
|---|---|---|---|
| `active_life_chapter` exists in runtime | `yes` | `backend/app/api/routes/transits.py::_attach_internal_period_reasoning_state(...)` injects `_active_life_chapter`; `backend/app/transit/present/public_builder.py` passes it into `build_period_core(...)` | This was missing before PR-SF1. |
| `semantic_focus_result` can choose `life_chapter` as source | `yes` | `backend/app/transit/narrative/period_semantic_focus.py::resolve_period_semantic_focus(...)`; tests in `backend/tests/test_period_semantic_focus.py` | Resolver precedence is already chapter-first when high-confidence chapter exists. |
| renderer consumes semantic focus | `yes` | `backend/app/transit/narrative/astrolog_narrative_engine.py::build_period_story(...)` and `_compose_semantic_focus_guidance(...)` | PR-4.1 made this visible in public prose. |
| debug exposes ownership | `yes` | `period_core["semantic_focus"]` in `deep_archetype_engine.py`; `PeriodNarrative.debug["semantic_focus"]`, `semantic_focus_consumed`, `composer_mode` in `astrolog_narrative_engine.py` | Ownership is now inspectable. |
| fallback works without chapter | `yes` | `backend/tests/test_astrolog_narrative_engine.py::test_period_story_semantic_focus_fallback_stays_legacy_when_missing` | No chapter does not break legacy rendering. |
| public payload remains additive/safe | `yes` | `backend/tests/_artifacts/reasoning_output_review/POST_PR_SF1_REVIEW.md`; `POST_PR_4_1_REVIEW.md` | No broad top-level public contract rewrite. |
| Aries 3rd proof test exists | `yes` | `test_resolver_prefers_life_chapter_semantic_focus_for_aries_3rd`; `test_period_story_consumes_semantic_focus_for_aries_3rd_saturn_return` | Covers resolver and renderer. |
| Cancer 8th proof test exists | `yes` | `test_resolver_prefers_life_chapter_for_cancer_8th`; `test_period_story_consumes_semantic_focus_for_cancer_8th_saturn_return` | Covers resolver and renderer. |
| Nodal activation proof test exists | `yes` | `test_resolver_prefers_life_chapter_for_nodal_activation_directional_logic`; `test_period_story_consumes_semantic_focus_for_nodal_direction` | Covers directional nodal logic. |

### Proof surfaces reviewed

- `backend/tests/_artifacts/reasoning_output_review/POST_PR_SF1_REVIEW.md`
- `backend/tests/_artifacts/reasoning_output_review/POST_PR_4_1_REVIEW.md`
- `backend/tests/test_period_semantic_focus.py`
- `backend/tests/test_astrolog_narrative_engine.py`
- `backend/tests/test_public_layered_output.py`
- `backend/tests/test_transit_narrative_public_payload.py`

## 3. Remaining Risks

### 3.1 Event selection is still event-first

Current selection still starts in:

- `backend/app/transit/narrative/selection.py::select_event_ids(...)`
- `backend/app/transit/narrative/daily_selection.py::select_daily_and_period_event_cards(...)`

This means the system still chooses **period cards/evidence** using salience, ranking, clustering, and score-like logic before chapter ownership is considered.

**Risk for PR-D v1:**
- chapter-owned prose may still coexist with event-first supporting cards
- selected event cards can still imply a different “owner feeling” than the chapter

**Assessment:**
- acceptable for PR-D v1 **if** event cards are explicitly treated as evidence, not rewritten as owner
- not acceptable for a global/default rollout without flag protection

### 3.2 PR-D override may conflict with selected event cards

`build_period_core(...)` still builds:

- `featured_events` from selected event cards
- `spine/support` event structure via renderer inputs

Even with chapter-owned semantic focus, the visible evidence layer remains event-derived.

**Risk:**
- PR-D v1 could make the chapter the semantic owner while event cards still look like the main period driver

**Assessment:**
- acceptable if PR-D v1 scope is explicitly:
  - semantic owner priority only
  - not event-card selection rewrite

### 3.3 Daily is still not chapter-aware

Daily still routes through:

- `backend/app/api/routes/transits.py`
- `backend/app/transit/narrative/daily_selection.py`
- `backend/app/transit/narrative/daily_synthesis.py`
- `backend/app/transit/narrative/today_story_candidate.py`

There is still no today-delta chapter ownership layer.

**Risk:**
- if PR-D v1 accidentally leaks chapter-first logic into daily, behavior drift will be hard to reason about

**Assessment:**
- daily must stay untouched in PR-D v1
- this is a strict boundary, not a soft preference

### 3.4 Extraction script still has a manual context path

`backend/scripts/dev/extract_reasoning_outputs.py` still builds `PeriodStoryContext(...)` manually in a way that bypasses the full runtime `build_period_core(...)` path.

**Risk:**
- artifact JSONs still show `period_core.semantic_focus = null`
- debug proof for runtime ownership can look stale unless read alongside the review markdown

**Assessment:**
- not a blocker for PR-D v1
- but it remains a tooling mismatch and should not be confused with runtime truth

### 3.5 Cancer 8th and nodal prose are correct but not final-polish complete

`POST_PR_4_1_REVIEW.md` shows:

- Cancer 8th is now clearly chapter-owned
- nodal Aries/Libra is now directionally correct
- both still have room for denser v4-grade prose

**Risk:**
- enabling PR-D v1 too broadly could freeze “correct but still thin” prose into more visible paths

**Assessment:**
- acceptable behind flag
- not yet a reason for default-on rollout

### 3.6 Structural T-square remains excluded

Structural T-square is still candidate/debug-only and not first-class active chapter parity.

**Assessment:**
- this is correct
- it should remain excluded from PR-D v1

## 4. Feature Flag Design

### Proposed flag

```text
LIFE_CHAPTER_PRIORITY_ENABLED=false
```

### Proposed config location

If implemented, the most natural location is:

- `backend/app/core/config.py`

as a boolean setting, similar to the existing transit/home toggles.

### Behavior when flag is `false`

Current behavior remains:

- event selection stays unchanged
- `active_life_chapter` may still be injected into runtime
- `resolve_period_semantic_focus(...)` may still use chapter semantics as a semantic focus source
- renderer may still consume semantic focus as it does now
- **no explicit chapter priority override is applied**
- selected event cards remain the practical visible evidence spine

This is effectively today’s post-PR-SF1 / PR-4.1 behavior.

### Behavior when flag is `true`

For allowed Tier-1 chapters only:

- `active_life_chapter` may become the **chapter-first period semantic owner**
- selected event cards remain visible, but are treated as **evidence/support**, not the owner
- renderer continues to use `semantic_focus_result` as it already does
- daily remains unchanged
- excluded chapter families remain excluded

### Guard conditions when flag is `true`

PR-D v1 should only apply chapter-first priority when all are true:

- `active_life_chapter` is present
- `chapter_type` is one of:
  - `saturn_return`
  - `nodal_return`
  - `nodal_activation`
- chapter confidence is high enough
- `semantic_focus_result.source == "life_chapter"`
- renderer path is already available

## 5. Minimal PR-D v1 Implementation Plan

This section is a plan only. Nothing here is implemented by this checkpoint.

### 5.1 Files to touch

- `backend/app/core/config.py`
  - add `LIFE_CHAPTER_PRIORITY_ENABLED` setting
- `backend/app/transit/narrative/deep_archetype_engine.py`
  - apply chapter-priority decision at period-core assembly time
- `backend/app/transit/narrative/astrolog_narrative_engine.py`
  - respect explicit chapter-priority owner markers in debug/composer mode if needed
- `backend/app/transit/present/public_builder.py`
  - only if additive debug/public summary exposure is needed
- tests:
  - `backend/tests/test_period_semantic_focus.py`
  - `backend/tests/test_astrolog_narrative_engine.py`
  - `backend/tests/test_public_layered_output.py`
  - `backend/tests/test_transit_narrative_public_payload.py`

### 5.2 Where priority override should happen

**Recommended location:**

- `backend/app/transit/narrative/deep_archetype_engine.py::build_period_core(...)`

This is the smallest safe place because it already has:

- selected event evidence (`selected_enriched`)
- `canonical_period_spine`
- `active_life_chapter`
- `semantic_focus_result`

### 5.3 What the override should do

When the flag is on and a Tier-1 chapter qualifies:

- mark the chapter as the semantic/period owner in `period_core` debug
- keep selected event cards as evidence/support
- do **not** rewrite `select_event_ids(...)`
- do **not** replace daily selection logic
- do **not** force structural chapter ownership

### 5.4 What the override should not do

- no rewrite of `backend/app/transit/narrative/selection.py::select_event_ids(...)`
- no rewrite of `backend/app/transit/narrative/daily_selection.py::select_daily_and_period_event_cards(...)`
- no best-times changes
- no daily ownership changes
- no public payload breaking changes

### 5.5 Minimal runtime behavior target

With flag on:

- period prose stays chapter-first where supported
- `period_core` / debug explicitly record chapter priority
- event cards remain evidence
- fallback without chapter still works unchanged

With flag off:

- current post-PR-4.1 behavior remains unchanged

### 5.6 Tests needed for PR-D v1

1. **Flag off regression**
- current Tier-1 behavior remains unchanged
- no daily drift
- no public payload break

2. **Flag on Tier-1 Saturn return**
- Aries 3rd remains `source=life_chapter`
- chapter priority marker is present
- event cards remain evidence/support

3. **Flag on Tier-1 Cancer 8th**
- chapter-first semantic owner is applied
- no event-selection rewrite occurs

4. **Flag on Tier-1 nodal activation**
- directional logic remains intact
- generic self/other balance does not return

5. **Excluded structural case**
- `structural_natal_chapter` does not become owner even with flag on

6. **Fallback no-chapter case**
- legacy path still works

### 5.7 Rollback strategy

Rollback should be trivial:

- set `LIFE_CHAPTER_PRIORITY_ENABLED=false`

Because PR-D v1 should be implemented as a narrow runtime branch rather than a destructive replacement, disabling the flag should restore current behavior without requiring event-selection rollback.

## 6. Go / No-Go Decision

### Decision

**`go behind flag only`**

### Why not `go`

Because the following are still true:

- event selection remains event-first
- daily is still not chapter-aware
- extraction tooling is not yet a perfect runtime mirror
- Cancer 8th and nodal copy are correct but not fully final-polish
- structural chapter ownership is not ready

### Why not `no-go`

Because the critical prereqs for a narrow Tier-1 flag rollout are already satisfied:

- runtime chapter injection exists
- resolver ownership exists
- renderer consumption exists
- debug visibility exists
- fallback exists
- additive payload safety exists
- Tier-1 proof tests exist

### Final checkpoint statement

**Broad PR-D remains no-go.**

**Scoped PR-D v1 is ready to plan and implement behind `LIFE_CHAPTER_PRIORITY_ENABLED=false` default, with scope limited to `saturn_return`, `nodal_return`, and `nodal_activation`.**
