# S2.1.5 — V26 LIVE Orphan Helper Residue Cleanup Design

## Scope

This is a bounded follow-up design artifact.

No code.
No runtime change.
No public schema change.
No endpoint/mobile change.
No live `core_story` package refactor.

This step exists because:

- S2.1.3 moved the live `core_story` branch into
  `backend/app/natal/narrative/core_story/`
- S2.1.4 removed the deprecated wrappers from the old V26 files
- the old files still contain helper residue that may now be orphaned

That residue must be handled separately from wrapper cleanup.

## 1. Current state after S2.1.4

Canonical live path:

- `backend/app/natal/narrative/core_story/plan_builder.py`
- `backend/app/natal/narrative/core_story/renderer.py`

Former live-symbol source files that still exist:

- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`

These files now contain historical residue only. That residue may include:

- private helper functions
- module-level constants
- dataclasses / type aliases
- imports that may now be dead

Some of that residue may be:

- true orphans
- locally referenced by other residue in the same file
- still meaningful as non-runtime compat material

That distinction must be audited before any deletion.

## 2. Goal

Determine whether residue left behind in the old V26 live files is:

1. **DELETE-safe now**
2. **FREEZE-only for a while**
3. **MIGRATE-callers-first**

The cleanup target is only the residue in the two former live files.

It is **not**:

- a rewrite of `core_story`
- a refactor of the new package
- a cleanup of unrelated legacy narrative systems
- a route/public output change

## 3. Audit questions

### 3.0 Starting point: reuse the S2.1.3 Step 0.5 audit

This audit should not start from zero.

Initial input should be the existing Step 0.5 artifact:

- `docs/system/audits/v26_live_core_story_helper_dependency_audit.md`

That audit already produced an `orphan-later` partition for both former
live files. S2.1.5 should:

- re-verify that partition **post-migration / post-wrapper-removal**
- tighten it into:
  - dead-truly
  - locally-residue-only
  - unexpected-live

This reduces drift and makes the residue audit explicitly continuous with
the earlier migration audit.

### 3.1 Caller truth

For every remaining residue symbol in:

- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`

trace all callers and partition into:

- used only by other residue in the same file
- imported/called elsewhere at runtime
- test-only
- dead/unreachable
- unclear

Scope here includes:

- private helper functions
- module-level constants
- dataclasses / type aliases
- imports that may now be dead

This step must explicitly catch non-function residue such as
`CORE_STORY_SECTIONS` or shadowed duplicate definitions.

### 3.1a Dead-import check

After S2.1.3 and S2.1.4, some imports in the former live files may now be
unused because the live roots and wrappers are gone.

This audit should explicitly classify imports into:

- still used by remaining residue
- dead-import residue
- unclear

Import cleanup should still remain a later implementation step, but the
audit must surface the exact dead-import set.

### 3.2 Runtime reachability

Confirm whether any current public endpoint or canonical builder path can
still reach any of this residue.

Expected answer after S2.1.4:

- live runtime should not depend on these helpers

But this must be verified, not assumed.

### 3.3 File-level end state

Decide whether the two files should become:

- fully deletable after residue cleanup
- minimal frozen stubs
- partially retained for some non-core-story purpose

## 4. Required output

Produce an audit report that includes:

- helper table
- non-function residue table
- import table
- caller table
- runtime reachability evidence
- delete/freeze/migrate recommendation per helper cluster
- file-level recommendation for each old V26 file

Suggested artifact:

- `docs/system/audits/v26_live_orphan_helper_audit.md`

## 5. Hard constraints

Any future implementation step based on this design must preserve:

- `response["core_story"]`
- `response["core_story_plan"]`
- `PublicNatalView.core_story`
- `profile_v8.identity_axis_body` fallback behavior
- `core_story_ui` inputs
- mobile / Chart Lab readers

This step must not:

- edit `backend/app/natal/narrative/core_story/`
- alter `natal_interpretation.py`
- widen scope into legacy/profile/transit/synastry cleanup

## 6. Test expectations for the later cleanup PR

If S2.1.5 later becomes implementation:

- keep compile checks on touched files
- rerun `backend/tests/test_natal_public_builder.py`
- rerun `backend/tests/test_composed_detail_renderer.py`
- keep existing S2.1.1 snapshot guards
- ensure no new caller imports old residue during cleanup

## 7. Recommendation

Recommended next bounded request:

- run an **orphan-helper trace audit** on the former V26 live files only

Not yet recommended:

- direct deletion of residue without caller partition
- any refactor of the new canonical `core_story` package

## Final recommendation

Proceed with **S2.1.5 audit-only** first.

Treat orphan residue cleanup as a separate tail step after migration and
wrapper removal, not as part of live `core_story` evolution.
