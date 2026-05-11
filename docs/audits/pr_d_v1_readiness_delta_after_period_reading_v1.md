# PR-D v1 Readiness Delta After `period_reading_v1`

Generated on 2026-05-06.

This is a **delta refresh only** against the previous checkpoint:

- [pr_d_v1_readiness_after_pr_sf1_pr_4_1.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/audits/pr_d_v1_readiness_after_pr_sf1_pr_4_1.md)

It focuses only on changes introduced by the additive organic period surface:

- `period_core.period_reading_v1`
- internal `composer_plan`
- organic guardrails on `blocks[]` / `full_text`
- legacy compatibility shadow fields

## 1. What Changed Since The Previous PR-D Checkpoint?

### New user-facing surface

The largest change is that the public period rendering surface is no longer effectively centered on:

- `period_opening`
- `big_picture`
- `mechanism`
- `growth_edge`
- `what_it_builds`

Those fields still exist, but the new primary user-facing surface is now:

- `period_core.period_reading_v1`

Current runtime evidence:

- [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py)
  - `build_period_story(...)`
  - `_compose_period_plan(...)`
  - `_build_period_reading_v1(...)`
  - `_legacy_fields_from_composer_plan(...)`
- [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py)
  - `result["period_reading_v1"] = dict(narr.period_reading_v1)`
- [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/present/public_builder.py)
  - preserves and normalizes nested `period_reading_v1`

### Internal source of truth is now clearer

The renderer now has a more explicit internal structure:

- `semantic_focus_result`
- `active_life_chapter.renderer_handoff`
- `composer_plan`
- `period_reading_v1.blocks`
- `period_reading_v1.full_text`
- legacy compatibility shadow fields

This is a meaningful change for PR-D readiness because the system now has a more visible and deterministic chain between:

- chapter-owned semantic selection
- internal composition plan
- public prose realization

### Legacy fields still remain

Legacy fields are still populated and are now derived from the same composer path:

- `period_opening`
- `big_picture`
- `mechanism`
- `growth_edge`
- `relational_or_life_expression`
- `what_it_builds`
- `core_story`
- `upper_meaning`

This matters for PR-D because teaser/mobile fallback paths are still alive and currently safe.

### Guardrails moved to the organic surface

Organic prose now has dedicated checks on:

- each `blocks[].text`
- `full_text`

Current implementation:

- [voice_guardrails_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/narrative/voice_guardrails_tr.py)
  - `find_organic_period_copy_issues(...)`
- [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py)
  - `_render_period_reading_guardrails(...)`

### EN path now preserves the new field

The English rewrite path no longer drops the nested surface:

- [public_voice_en.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/public_voice_en.py)
  - `rewrite_period_core_en(...)`

This is still a preserve/humanize path, not a fully equivalent organic EN composer.

### Extraction and review artifacts are now aligned to the new surface

Current extraction path now records:

- `period_narrative_prose.period_reading_v1`
- `debug.composer_plan`
- `debug.period_reading_v1_guardrails`

Evidence:

- [extract_reasoning_outputs.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/scripts/dev/extract_reasoning_outputs.py)
- [POST_PR_ORGANIC_PERIOD_READING_REVIEW.md](/Users/sahradenizozdogan/Astrologi-Ai/backend/tests/_artifacts/reasoning_output_review/POST_PR_ORGANIC_PERIOD_READING_REVIEW.md)

## 2. Does `period_reading_v1` Make PR-D Safer Or Riskier?

## Safer overall

`period_reading_v1` makes a scoped PR-D v1 **safer**, not riskier.

### Why safer

1. If PR-D makes Tier-1 LifeChapter cases chapter-first, the output now has a clear realization surface.
   - Before: chapter ownership could be correct while public prose still felt segmented/generic.
   - Now: chapter-owned semantic focus already flows into `composer_plan -> period_reading_v1`.

2. `semantic_focus.source == "life_chapter"` still flows into the organic output.
   - Tier-1 evidence remains present in current code and tests.
   - Guided cases still produce `composer_mode = "semantic_focus_guided"`.

3. Legacy fields remain available for compatibility.
   - teaser and current mobile fallback paths are not broken
   - PR-D does not need a simultaneous surface migration

4. Public payload remains additive-safe.
   - `PublicTransitResponse.period_core` is still an untyped `dict`
   - nested additive field under `period_core` remains safe

5. Mobile still requires no immediate change.
   - current `PeriodCoreDto` still only reads:
     - `title`
     - `core_story`
     - `upper_meaning`
     - `big_picture`
     - `mechanism`
     - `tags`
   - it does **not** yet consume `period_reading_v1`
   - therefore backend PR-D work can still happen behind flag without forcing Phase 2 mobile coordination

### Remaining caution

`period_reading_v1` does not reduce the main architectural PR-D risk:

- event selection is still event-first

So the output layer is safer, but the authority-routing decision still must be feature-flagged.

## 3. Re-check PR-D v1 Scope

### Still allowed

- `saturn_return`
- `nodal_return`
- `nodal_activation`

### Still excluded

- `structural_natal_chapter`
- `profection_year`
- `progressed_lunation`
- `solar_return_theme` as owner
- `outer_planet_angle_hit`
- daily chapter ownership
- best-times / opportunity

### Scope status after `period_reading_v1`

No change.

`period_reading_v1` improves realization, but does not widen the safe owner set.

Structural T-square remains correctly excluded:

- non-LifeChapter fallback now renders through `period_reading_v1`
- but that does **not** make `structural_natal_chapter` owner-ready

## 4. Re-check Blockers

## 4.1 Event selection is still event-first

No change from the earlier checkpoint.

PR-D still must not rewrite:

- `selection.py`
- daily/period card scoring
- event ranking ownership

`period_reading_v1` does not solve this; it only makes chapter-first realization safer once semantic ownership is chosen.

## 4.2 Daily is still not chapter-aware

No change.

Current daily remains outside this scope:

- `daily_selection.py`
- `daily_synthesis.py`
- `today_story_candidate.py`

`period_reading_v1` is period-only and additive.

## 4.3 Non-LifeChapter fallback prose is still thinner

This is the most important new nuance.

The new universal output surface means:

- all period cases now emit `period_reading_v1`
- fallback/non-LifeChapter prose is structurally organic
- but it is still stylistically thinner than guided Tier-1 chapter-owned cases

This is **not** a PR-D blocker for Tier-1 scoped rollout, because PR-D v1 scope does not promote those fallback families into chapter-first owners.

## 4.4 Extraction/manual paths

This blocker improved, but did not disappear entirely.

What improved:

- extraction now includes `period_reading_v1`
- organic output is visible in artifacts

What remains:

- extraction still uses manual context construction in parts
- it is still not a perfect mirror of the full route/runtime public payload path

Assessment:

- better than before
- still not a blocker for PR-D v1

## 4.5 `public_voice_en` is still preserve-only

No major change in readiness conclusion.

Current EN path:

- preserves `period_reading_v1`
- lightly humanizes nested block texts
- recomputes nested `full_text`

It does **not** provide full organic parity with TR.

Assessment:

- acceptable for PR-D v1 behind flag
- not a blocker for scoped TR-first owner rollout

## 4.6 `period_reading_v1` universal production

This is a positive delta, not a blocker.

The fact that `period_reading_v1` is universal means PR-D does not need a separate “guided-only surface”.

That reduces implementation complexity:

- no bifurcated public shape
- no chapter-only rendering branch
- same public surface regardless of whether chapter-first is active

## 4.7 Legacy fields compatibility

This remains a positive constraint and a design requirement.

PR-D must not reintroduce a split where:

- `period_reading_v1` is chapter-first
- but legacy fields are still generated differently

Current code already routes both through the same composer plan. PR-D should preserve that property.

## 5. PR-D Implementation Implication After `period_reading_v1`

This is the most important implementation delta.

### Previous PR-D plan emphasis

The older checkpoint correctly said chapter priority should influence:

- `active_life_chapter`
- `semantic_focus_result`
- `build_period_core(...)`

### Updated implementation target

After `period_reading_v1`, PR-D should target this chain:

1. `active_life_chapter`
2. `semantic_focus_result`
3. `composer_plan`
4. `period_reading_v1`
5. legacy shadow fields derived from the same composer plan

### Where priority should influence happen now

Still recommended:

- [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py)
  - `build_period_core(...)`

Reason:

- this is where selected event evidence, `canonical_period_spine`, `active_life_chapter`, and `semantic_focus_result` already converge
- it remains the smallest safe place to introduce chapter-first owner priority

### What PR-D should now target

PR-D should **not** target legacy period fields directly.

It should target:

- which source becomes semantic owner in `semantic_focus_result`
- how that owner flows into `composer_plan`
- how `period_reading_v1` realizes the owner

Legacy fields should remain downstream compatibility shadows.

### What must not change

- event selection algorithm
- daily behavior
- natal behavior
- top-level public payload shape
- excluded chapter families
- structural T-square ownership

### How to keep legacy fields aligned

Hard requirement:

- PR-D must preserve the existing single-source-of-truth property:
  - `semantic_focus_result -> composer_plan -> period_reading_v1 + legacy fields`

PR-D must not add:

- a separate chapter-only renderer for `period_reading_v1`
- a separate fallback renderer for legacy fields

## 6. Updated Go / No-Go Decision

**Decision: `go behind flag only`**

This decision does **not** change from the previous checkpoint.

### Why it stays `go behind flag only`

- runtime chapter ownership prerequisites still exist
- organic public surface is now stronger and safer
- Tier-1 chapter-owned cases are now realized through `period_reading_v1`
- compatibility paths remain safe
- mobile still does not require an immediate migration

### Why it is still not `go`

- event selection is still event-first
- daily remains outside chapter ownership
- fallback prose outside guided Tier-1 cases is still thinner
- EN path is preserve-only

So the delta is favorable, but it is still not a default-on justification.

## 7. Minimal PR-D v1 Plan Update

## Files to touch

Same core runtime files as before, but with one important emphasis shift:

- `backend/app/core/config.py`
  - add `LIFE_CHAPTER_PRIORITY_ENABLED`
- `backend/app/transit/narrative/deep_archetype_engine.py`
  - chapter-first owner priority branch in `build_period_core(...)`
- `backend/app/transit/narrative/period_semantic_focus.py`
  - only if owner metadata or confidence gating needs a narrow extension
- `backend/app/transit/narrative/astrolog_narrative_engine.py`
  - only to preserve or expose owner/debug markers if needed
- `backend/app/transit/present/public_builder.py`
  - only if an additive debug breadcrumb is needed in `period_core`

### Tests to add or update

- `backend/tests/test_period_semantic_focus.py`
  - chapter-first owner branch under flag
- `backend/tests/test_astrolog_narrative_engine.py`
  - ensure `semantic_focus_guided` remains chapter-owned under flag
- `backend/tests/test_period_reading_v1_contract.py`
  - ensure chapter-first Tier-1 cases still produce correct `period_reading_v1`
  - ensure legacy fields remain aligned from the same composer path
- `backend/tests/test_public_layered_output.py`
  - additive-safe payload remains intact
- `backend/tests/test_transit_narrative_public_payload.py`
  - flag-off behavior unchanged
  - flag-on Tier-1 semantics reflected without top-level schema break

### Sample review cases

Keep the same proof cases:

- Aries 3rd Saturn return + South Node overlap
- Cancer 8th Saturn return
- Nodal activation NN Aries / SN Libra

Still include one fallback/non-owner control case:

- structural T-square

Reason:

- confirms the flag promotes only Tier-1 chapter-first cases
- confirms excluded structural cases remain fallback/non-owner

### Rollback strategy

Unchanged in principle, but simpler in practice now.

Set:

```text
LIFE_CHAPTER_PRIORITY_ENABLED=false
```

That should restore the current post-organic behavior because:

- `period_reading_v1` remains live either way
- the only thing changing under PR-D should be owner priority, not the rendering surface shape

### Net implementation delta vs the previous PR-D plan

The older plan was already correct about the flag and scope.

The only material update is:

**PR-D should now be implemented as chapter-first semantic ownership flowing into `semantic_focus_result -> composer_plan -> period_reading_v1`, not as a change framed around legacy segment fields.**

## Final Delta Conclusion

`period_reading_v1` makes PR-D v1 **safer to implement behind flag** because the renderer now has a coherent public realization surface for chapter-first semantic ownership.

It does **not** remove the need for:

- strict Tier-1 scope
- feature flag default-off
- no daily changes
- no event selection rewrite

So the updated decision remains:

**`go behind flag only`**
