# Codex Prompt — Path 3 Locked: PR-4 Continues, PR-A Starts LifeChapter Contract

**For:** Codex
**From:** Sahra (voice lead)
**Date:** 2026-05-04
**Status:** Decision locked. Supersedes the standalone PR-4 prompt (`codex_prompt_pr4_renderer_migration.md`) — chapter-ready constraint is now embedded.

---

## Summary

Proceed on two parallel tracks:

- **Track A: PR-4 renderer migration continues now.**
  It stays focused on the **current canonical chain** and the v4 target voice reference.
- **Track B: PR-A starts the LifeChapter architecture line.**
  It is **contract-only**, with **no runtime behavior change**.

This keeps momentum on prose quality while starting the missing astrolog-thinking layer above event selection.

## Key Decisions

- **Do not block PR-4.**
- **Do not implement full `LifeChapterDetector` yet.**
- **Do not add profection / progression / solar return engines yet.**
- **Do not change daily behavior yet.**
- **Do not pre-design `PeriodSemanticFocusResolver` in PR-A.** SemanticFocus waits until LifeChapter contract and detector skeleton exist.
- **PR-D must be feature-flagged** when chapter priority eventually changes runtime behavior.
- **LifeChapter lint must reuse `voice_guardrails_tr.py` infrastructure.** No new lint engine.

---

## Track A — PR-4 Renderer Migration

### Goal

Make the current renderer produce period prose closer to `docs/voice/handcrafted_period_validation_v4_final.md`, using the **existing event-led canonical chain**.

### Constraint clarification

PR-4 should **faithfully render the current chain**. Event-led selection is acceptable for this PR.

The forward-compatibility rule is:

- renderer context must be able to accept an **optional** `active_life_chapter: None | LifeChapter`
- renderer must **not** invent chapter-level meaning when `active_life_chapter is None`
- renderer must **not crash** when chapter fields are absent
- renderer's semantic owner remains:
  - `canonical_period_spine`
  - current/future `semantic_focus`
  - `period_voice_policy`
- events remain **evidence/input**, not the long-term semantic owner

### Required PR-4 shape

- Keep current canonical inputs as the only required inputs.
- Add only **optional future-ready slots** in internal context/debug shape:
  - `active_life_chapter`
  - `chapter_type`
  - `chapter_phase`
  - `chapter_selected_meaning`
- Do not branch renderer logic on chapter presence yet beyond safe passthrough / no-op compatibility.
- Do not couple PR-4 to LifeChapter rollout timing.

### PR-4 non-goals

- no chapter selection logic
- no chapter priority override
- no daily changes
- no Best Times / Opportunity logic

---

## Track B — PR-A LifeChapter Contract

### Scope

PR-A must stay small.

It includes only:

1. `docs/system/life_chapter_signal_registry.md`
2. `backend/app/transit/narrative/life_chapter_contract.py`
3. contract-only tests
4. optional doc references if needed for clarity

It does **not** include:

- detector logic
- selection changes
- priority changes
- semantic focus coupling
- new scoring
- new annual technique engines
- new lint subsystem

### Contract format

Use a **lightweight contract file** in `backend/app/transit/narrative/life_chapter_contract.py`.

Recommended shape:

- mirror repo style by using a **small internal contract module**
- keep it internal and non-wired
- expose:
  - chapter type constants / enum
  - `LifeChapter` data shape
  - tiny validator/helper if needed
- no runtime integration yet

### Initial chapter taxonomy

Start with **11 chapter types** now, not 9:

- `saturn_return`
- `jupiter_return`
- `nodal_return`
- `nodal_activation`
- `profection_year`
- `progressed_lunation`
- `solar_return_theme`
- `outer_planet_angle_hit`
- `eclipse_activation`
- `major_transit_chapter`
- `structural_natal_chapter`

Rationale:

- `nodal_return` and `nodal_activation` are not the same
- Chart 4 class patterns need `structural_natal_chapter`
- adding them later would force contract churn

### Contract fields

PR-A contract should include:

- `version`
- `chapter_id`
- `chapter_type`
- `domain`
- `spine_line`
- `time_window`
- `phase`
- `activated_natal_factors`
- `core_question`
- `selected_meaning`
- `evidence[]`
- `suppressed_readings[]`
- `priority`
- `confidence`
- `debug`

Rules:

- `evidence[]` is required
- `suppressed_readings[]` is required
- `selected_meaning` must be natal-specific, not generic cookbook astrology
- no prediction/outcome claims

### Registry doc contents

`life_chapter_signal_registry.md` should:

- catalog current available signals only
- mark each as:
  - live
  - partial
  - missing
- distinguish:
  - `signal exists`
  - `signal is period owner`
- explicitly list future-missing sources:
  - profection
  - time lord
  - progressed Moon
  - progressed lunation
  - solar return as owner
- keep this as readonly catalog, not implementation spec drift

---

## PR-B / PR-C / PR-D Sequence

### PR-B — LifeChapterDetector skeleton

- add detector facade only
- return `active_life_chapter | None`
- no selection priority change yet
- no semantic focus integration yet

### PR-C — Tier-1 detection

Implement only:

- `saturn_return`
- `nodal_activation`
- `nodal_return`

Add:

- overlap signals like Saturn return + South Node same sign/house
- phase model:
  - `approaching`
  - `first_pass`
  - `retrograde_review`
  - `final_pass`
  - `integrating`
  - `background`

### PR-D — Period-core integration

- active LifeChapter can outrank generic transit period
- this is the first meaningful runtime behavior change
- **must ship behind a feature flag**
- default:
  - `LIFE_CHAPTER_PRIORITY_ENABLED = false`

Flag rule:

- when disabled, current period behavior is unchanged
- when enabled, chapter priority can override generic event-led selection

### PR-E later

- profection
- time lord
- progressed Moon / progressed lunation
- solar return as owner

### PR-F later

- daily trigger attaches to active LifeChapter
- no daily prose redesign yet, only chapter reference plumbing

---

## Test Plan

### PR-A tests

Only contract-level tests:

- minimal `LifeChapter` can instantiate / validate
- `chapter_type` must be one of the 11 allowed types
- `evidence[]` must exist and be non-empty
- `suppressed_readings[]` must exist
- `selected_meaning` fails if it contains prediction/outcome language

### Guardrail rule

Reuse existing `voice_guardrails_tr.py` infrastructure.

Add a small LifeChapter-specific ban set such as:

- guaranteed outcomes
- predictive phrasing
- fate-certainty phrasing

Do **not** create a new lint engine.

### PR-D future tests

Reserve for later:

- LifeChapter outranks normal transit period when flag is on
- no behavior change when flag is off
- South Node overlap increases relevance
- chapter phase identified correctly
- no prediction language in chapter meaning

---

## Assumptions and Defaults

- `SHOU_VOICE_VNEXT.md` remains the canonical voice spec in this repo.
- PR-4 renderer work continues against the **current** canonical chain.
- LifeChapter is an **upstream reasoning layer**, not a renderer concern.
- `PeriodSemanticFocusResolver` is intentionally deferred until after PR-A / PR-B.
- The first useful LifeChapter implementation should target **Saturn return + nodal activation**, not annual techniques.
- Runtime compatibility matters more than completeness in the first LifeChapter pass.

---

## Supersedes

- `codex_prompt_pr4_renderer_migration.md` — chapter-ready constraint not embedded there. Use this doc as the PR-4 source of truth.
- `codex_prompt_period_lifechapter_audit.md` — audit complete; outcome consumed into this plan. Audit doc remains as historical reference under `docs/system/period_calculation_life_chapter_audit.md`.

## Decision authority

Sahra (voice lead). Codex flags scope/sequencing concerns; Sahra final call on every PR scope.

---

*Path 3 locked — PR-4 continues chapter-ready, PR-A starts LifeChapter contract in parallel.*
