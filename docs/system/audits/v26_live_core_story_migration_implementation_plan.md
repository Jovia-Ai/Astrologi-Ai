# S2.1.3 — V26 LIVE Core Story Migration Implementation Plan

## Scope

This is an implementation-planning artifact only.

No code.
No runtime change.
No deletion.
No refactor executed by this document.

This plan assumes S2.1.2 was accepted and the chosen migration target is:

- **Option B — dedicated `core_story/` sub-package**

Goal:

- relocate the live `core_story` branch out of V26/legacy-named files
- preserve all public and downstream contracts
- use a wrapper-first transition
- prove parity before any legacy cleanup

Out of scope:

- any wording rewrite
- any public schema change
- endpoint or mobile changes
- Chart Lab contract changes
- ARC/A2 merge
- Phase-4 / deep_read work

## 1. Migration target

Planned new home:

- `backend/app/natal/narrative/core_story/`

Planned package shape:

- `backend/app/natal/narrative/core_story/__init__.py`
- `backend/app/natal/narrative/core_story/plan_builder.py`
- `backend/app/natal/narrative/core_story/renderer.py`

Target symbols to move:

- `build_core_story_plan(...)`
- `render_core_story(...)`

The old locations remain temporarily as compatibility wrappers:

- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`

This is a relocation plan, not a semantic rewrite.

Why sub-package instead of one module:

- Step 0.5 helper audit found a cross-file name collision risk:
  both move-with sets contain a private helper named `_headline_ref`
- keeping the plan-builder helpers and renderer helpers in separate modules
  avoids introducing a new shadowing bug during migration
- this preserves the textual-faithfulness-first rule without forcing helper
  renames during extraction

## 2. Hard invariants

The migration is allowed only if all of the following stay true:

- `response["core_story"]` stays byte-compatible
- `response["core_story_plan"]` schema stays compatible
- `PublicNatalView.core_story` stays unchanged in shape and content
- `profile_v8.identity_axis_body` fallback semantics stay unchanged
- mobile and Chart Lab consumer behavior stays unchanged
- no public field set changes in `/interpret/ui`
- no route changes

## 3. Proposed file touch map

Primary implementation files:

- `backend/app/natal/narrative/core_story/__init__.py`
- `backend/app/natal/narrative/core_story/plan_builder.py`
- `backend/app/natal/narrative/core_story/renderer.py`
- `backend/app/api/routes/natal_interpretation.py`
- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`

Likely test files:

- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_natal_interpretation.py` if route-level parity lives there
- dedicated new test file if import-compat parity is cleaner isolated

Files explicitly not to touch in S2.1.3:

- `backend/app/natal/public_models.py`
- mobile files
- endpoint definitions
- `profile_v8_payload_builder.py` behavior
- ARC/scorer files
- deep_read / Phase-4 renderer files

## 4. Recommended migration sequence

### Step 0 — Preconditions

Required before code starts:

- S2.1.1 snapshot coverage remains green
- S2.1.2 design decision accepted
- V26 dead branch already removed in S2.2

### Step 1 — Create dedicated module

Add new sub-package:

- `backend/app/natal/narrative/core_story/`

Internal split:

- `plan_builder.py`
  - `build_core_story_plan(...)`
  - narrative-binding move-with helper set from Step 0.5
- `renderer.py`
  - `render_core_story(...)`
  - narrative-renderer move-with helper set from Step 0.5
- `__init__.py`
  - exports the two public symbols only

Initial content:

- exact moved implementation of:
  - `build_core_story_plan(...)`
  - `render_core_story(...)`
- only the private helpers they directly need

Rule:

- no cleanup, no renaming for clarity, no behavioral normalization in the
  same change
- first extraction should be as textually faithful as possible

### Step 2 — Add compatibility wrappers

Keep old import paths alive:

- `narrative_binding.build_core_story_plan(...)`
- `narrative_renderer_v26.render_core_story(...)`

But change them into thin wrappers that delegate to:

- `natal.narrative.core_story.build_core_story_plan(...)`
- `natal.narrative.core_story.render_core_story(...)`

Rule:

- wrappers must not alter arguments
- wrappers must not alter return values
- wrappers must not add migration-specific branching

Why:

- preserves existing callers
- makes parity testable directly
- keeps rollback cheap

### Step 3 — Add import-compat parity guard

Before rewiring route imports, add a direct parity test:

- old import path and new import path
- same fixture
- same inputs
- exact equality for:
  - `core_story_plan`
  - `core_story`

This guard closes a different risk than public snapshots:

- route snapshots prove app-facing output parity
- import-compat parity proves wrappers themselves are transparent

### Step 4 — Rewire canonical caller

Only after Step 3 passes:

- update `backend/app/api/routes/natal_interpretation.py`

Preferred import direction after rewire:

- import directly from `natal.narrative.core_story`

Wrappers remain temporarily in old locations for:

- rollback
- compatibility
- staged cleanup

### Step 5 — Verify route/public parity

Run and keep green:

- existing S2.1.1 snapshot tests
- route-level parity tests on `/interpret/ui`
- public field-set no-op test
- `profile_v8.identity_axis_body` fallback parity test

### Step 6 — Defer cleanup

Do not remove wrappers in the same change unless explicitly approved.

Wrapper removal should be a separate follow-up only after:

- import-compat parity proved
- route/public parity proved
- no downstream drift observed

## 5. Test plan

### Required existing guards to keep

- `public["core_story"]` content + shape snapshot
- `response["core_story_plan"]` schema snapshot
- `profile_v8.identity_axis.body` fallback snapshot

### New required guards for S2.1.3

#### A. Import-compat parity test

Inputs:

- same canonical fixture used in S2.1.1 where possible

Assertions:

- old `build_core_story_plan(...)` == new `build_core_story_plan(...)`
- old `render_core_story(...)` == new `render_core_story(...)`

This is the extra guard requested after S2.1.2 review.

#### B. Route-level parity test

Assertions:

- `/interpret/ui` payload public field set unchanged
- `public["core_story"]` byte-equal
- `response["core_story_plan"]` schema-compatible and unchanged on locked
  fixture

#### C. Downstream fallback parity test

Assertions:

- `profile_v8.identity_axis_body` still resolves identically from
  `core_story_ui.text` or `core_story`

#### D. Negative drift test

Assertions:

- no accidental change in public payload field set
- no accidental import of signature-renderer-only structures into
  `core_story`

## 6. Rollback strategy

Rollback must stay cheap.

Planned rollback path:

1. revert direct caller import in `natal_interpretation.py`
2. keep wrappers intact
3. old symbol locations continue serving runtime

This is why wrappers should survive the first migration PR.

If parity fails:

- do not continue to cleanup
- do not remove wrappers
- revert caller rewiring only

## 7. Risk notes

### Risk 1 — semantic drift hidden inside extraction

Even a “simple move” can change behavior if helper dependencies are moved
selectively or normalized during extraction.

Mitigation:

- textual-faithfulness-first extraction
- import-compat parity test before route rewiring

### Risk 2 — contract drift in `core_story_plan.debug`

`data_quality` and debug consumers use nested keys under
`core_story_plan.debug`.

Mitigation:

- schema snapshot guard
- no opportunistic cleanup during migration

### Risk 3 — public parity passes but wrapper path drifts

The route may pass while legacy import paths become subtly non-identical.

Mitigation:

- dedicated import-compat parity test

### Risk 4 — premature cleanup

Deleting wrappers in the same PR would make rollback noisy and broaden
scope.

Mitigation:

- cleanup deferred to a later, separately approved step

## 8. Approval gate for implementation

S2.1.3 implementation should be approved only if all of the following are
accepted:

- new home is `backend/app/natal/narrative/core_story/`
- wrappers stay for the first migration step
- import-compat parity test is mandatory
- route/public snapshot parity remains mandatory
- cleanup is explicitly deferred

## 9. Expected deliverable shape for the later implementation PR

One bounded PR:

- new `core_story/` sub-package
- wrapper conversion in old files
- caller rewire in natal route
- parity tests
- no payload change
- no cleanup deletion

Follow-up PR, only if separately approved:

- remove wrappers
- remove legacy live symbol shells

## Final implementation direction

Proceed with:

- **wrapper-first migration to dedicated `core_story/` sub-package**

Required proof before any cleanup:

- **import-compat parity**
- **route/public snapshot parity**
