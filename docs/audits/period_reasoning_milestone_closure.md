# Period Reasoning Milestone Closure — SHOU Backend

## 1. Executive Summary

- The old period stack was materially event-first and scoring-heavy: selected event cards, policy fallbacks, and renderer behavior together determined meaning, often without a single explicit semantic owner.
- The runtime period path now has a clearer semantic chain: `active_life_chapter` can enter runtime, `semantic_focus_result` can select `life_chapter` as owner, renderer builds from that, and public period prose is realized through `period_reading_v1`.
- The renderer is no longer expected to invent meaning by itself; it now composes from semantic focus, chapter handoff, and an internal `composer_plan`.
- `period_core.period_reading_v1` is now the additive organic user-facing period surface, while old segmented period fields remain populated as compatibility shadows.
- Tier-1 LifeChapter priority now exists behind `LIFE_CHAPTER_PRIORITY_ENABLED=false` by default; it is implemented but not enabled globally.
- Allowed PR-D v1 owner types are limited to `saturn_return`, `nodal_return`, and `nodal_activation`.
- Event selection, daily reasoning, natal reasoning, and top-level public schema were not broadly rewritten as part of this milestone.
- This milestone closes the period semantic ownership and public realization foundation, not the full rewrite of all reasoning surfaces.

## 2. Completed Work

## PR-SF1 PeriodSemanticFocusResolver

What it added:
- Runtime `_active_life_chapter` wiring into the live period path.
- `PeriodSemanticFocusResolver` and `PeriodSemanticFocusResult`.
- A single explicit semantic-focus contract that can select `life_chapter` as source for strong Tier-1 cases.

Why it mattered:
- It ended the prior fragmentation where meaning ownership was split across event selection, voice policy, and renderer fallback behavior.
- It made period semantic ownership visible in debug and available to downstream composition.

What it did not change:
- It did not rewrite event selection.
- It did not enable LifeChapter priority by itself.
- It did not rewrite daily or natal.

## PR-4.1 Renderer Semantic Focus Consumption

What it added:
- Renderer consumption of `semantic_focus_result`.
- Renderer use of `active_life_chapter.renderer_handoff` for guided Tier-1 prose.
- Debug markers showing whether semantic focus was actually consumed.

Why it mattered:
- Semantic ownership stopped being only an upstream/debug concept and began shaping public prose.
- Tier-1 cases such as Aries 3rd, Cancer 8th, and nodal direction started rendering as chapter-owned readings instead of generic scaffolds.

What it did not change:
- It did not create a separate chapter-only renderer.
- It did not change selection ranking.
- It did not change daily.

## PR-4 Organic `period_reading_v1`

What it added:
- `period_core.period_reading_v1` as the new additive organic reading surface.
- Internal `composer_plan` as the single source of truth for:
  - `period_reading_v1.blocks`
  - `period_reading_v1.full_text`
  - legacy compatibility shadow fields
- Organic guardrails on `blocks[]` and `full_text`.

Why it mattered:
- The public period voice surface is no longer structurally tied to the old segmented field model.
- Meaning realization now has a clearer internal chain and a better mobile-first target surface.

What it did not change:
- It did not remove legacy fields.
- It did not require immediate mobile changes.
- It did not produce full EN organic parity.

## PR-D v1 Feature-Flagged Tier-1 Priority

What it added:
- `LIFE_CHAPTER_PRIORITY_ENABLED=false` by default.
- A chapter-priority gate for allowed Tier-1 chapter types.
- `chapter_priority` debug state in `period_core`.
- Evidence/support marking for featured events when chapter priority applies.

Why it mattered:
- The system can now explicitly mark chapter-first ownership for allowed Tier-1 cases without creating a separate renderer path.
- This turns the semantic ownership chain into a controlled rollout path rather than a purely conceptual readiness state.

What it did not change:
- It did not enable the flag by default.
- It did not rewrite selection.
- It did not include structural chapter ownership.
- It did not change daily, natal, or best-times behavior.

## 3. Current Runtime Chain

The current conceptual runtime chain is:

`active_life_chapter`
→ `semantic_focus_result`
→ `chapter_priority gate`
→ `composer_plan`
→ `period_reading_v1`
→ `legacy compatibility shadows`

Event cards now fit into this system as follows:

- They are still selected by the old event-first system.
- They remain visible in `featured_events`.
- When PR-D flag applies, they are treated as `evidence_support`, not as the primary semantic owner.

This is the key architecture change of the milestone: event cards still matter, but meaning ownership no longer has to come from them.

## 4. Current Public Surface

`period_core.period_reading_v1` is now the new organic user-facing period surface.

It currently carries:
- `blocks[]`
- `full_text`

`full_text` is the canonical reading surface, while `blocks[]` preserve paragraph/role structure for future UI use.

Legacy fields still remain populated:
- `period_opening`
- `big_picture`
- `mechanism`
- `growth_edge`
- `relational_or_life_expression`
- `what_it_builds`
- `core_story`
- `upper_meaning`

These old fields are now compatibility shadows, not the target voice surface.

Mobile Phase 1 does not require change because:
- the new surface is additive under `period_core`
- legacy/fallback fields still exist
- top-level public schema was not broken

## 5. Feature Flag Status

Current flag status:
- `LIFE_CHAPTER_PRIORITY_ENABLED=false`

When `false`:
- current post-organic behavior remains active
- `semantic_focus_result` may still source `life_chapter`
- renderer may still produce chapter-owned Tier-1 prose
- no explicit chapter-priority override is applied

When `true`:
- eligible Tier-1 LifeChapter cases can become chapter-first semantic owners
- renderer still uses the same semantic-focus/composer path
- `period_reading_v1` remains the public realization surface
- legacy fields remain derived from the same composer plan

Allowed chapter types:
- `saturn_return`
- `nodal_return`
- `nodal_activation`

Excluded chapter types:
- `structural_natal_chapter`
- `profection_year`
- `progressed_lunation`
- `solar_return_theme`
- `outer_planet_angle_hit`

Also excluded from this flag scope:
- daily chapter ownership
- best-times / opportunity ownership

## 6. What Is Intentionally Not Solved Yet

- Event selection is still event-first.
- Daily is not chapter-aware.
- `structural_natal_chapter` remains excluded.
- Non-LifeChapter fallback prose is still thinner than guided Tier-1 prose.
- EN path is preserve-safe, not full organic parity.
- Mobile `period_reading_v1` adoption is still pending.

These are not accidental omissions; they were deliberately left out of this milestone to keep semantic ownership, renderer realization, and chapter-priority rollout scoped and testable.

## 7. Remaining Risks

- Event cards and chapter owner can still feel mixed until the event evidence layer is redesigned more explicitly.
- Daily can still diverge from the period owner model because it remains on an older reasoning path.
- Non-LifeChapter fallback prose still needs more density and specificity.
- Extraction/review scripts may not perfectly mirror the full runtime path in every branch, so some artifacts still need to be read with runtime-aware caution.

## 8. Validation Snapshot

Recent validation runs confirmed:

- PR-4 Organic `period_reading_v1`:
  - `162 passed`
  - `period_reading_v1` exists for Tier-1 and fallback period outputs.
  - Legacy fields remain populated.

- PR-D v1 flag implementation:
  - `169 passed`
  - flag default is `false`
  - flag on applies only to `saturn_return`, `nodal_return`, `nodal_activation`
  - `structural_natal_chapter` remains excluded
  - event cards are marked `evidence_support` when chapter priority applies

## 9. Recommended Next Milestones

1. Mobile Phase 2: consume `period_reading_v1`
2. Daily `today_delta_signal` / chapter-aware daily
3. Non-LifeChapter fallback density
4. Structural chapter PR-C.4
5. EN organic parity
6. Timing / Opportunity Engine

## 10. One-line Handoff

The period proof surface is no longer primarily event-story prose. It now has a chapter-aware semantic owner, an explicit semantic focus contract, an organic period_reading_v1 public surface, and a feature-flagged Tier-1 chapter-priority path.
