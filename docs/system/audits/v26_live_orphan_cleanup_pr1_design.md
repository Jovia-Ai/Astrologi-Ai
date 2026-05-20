# S2.1.6 — V26 LIVE Orphan Cleanup PR-1 Design

## Scope

This is a design-only artifact for the first bounded cleanup PR after
S2.1.5.

No code in this document.
No runtime change in this document.
No public schema change in this document.

This design uses as source of truth:

- `docs/system/audits/v26_live_orphan_helper_audit.md`

## 1. Goal

PR-1 should remove only the safest, most obviously dead residue left in
the former V26 live files, plus fix stale non-canonical test imports that
now point at removed symbols.

This PR is intentionally **narrow**.

### In scope

- `dead-truly` residue only
- dead-import cleanup directly caused by that removal
- stale `tests/engine/*` imports that still reference removed
  `build_narrative`

### Out of scope

- `locally-residue-only` helper clusters
- any cleanup inside `backend/app/natal/narrative/core_story/`
- route changes
- endpoint/mobile changes
- public output changes
- ARC/A2 work
- Phase-4 / deep_read work

## 2. Why PR-1 is separate

The S2.1.5 audit showed:

- `unexpected-live = none`
- canonical runtime is already off the old V26 live files
- but residue size is still large

If we mixed dead-truly cleanup with the large locally-residue-only
clusters, the PR would become effectively file-wide deletion. That is not
the right first cleanup step.

PR-1 therefore removes only:

1. symbols that are already dead-truly
2. imports made dead by their removal
3. stale non-canonical tests that still import removed legacy symbols

## 3. Proposed touch set

### 3.1 Former V26 live files

- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`

### 3.2 Stale test files

- `tests/engine/test_narrative_binding.py`
- `tests/engine/test_narrative_voice_invariants.py`

### 3.3 Not touched

- `backend/app/natal/narrative/core_story/`
- `backend/app/api/routes/natal_interpretation.py`
- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_composed_detail_renderer.py`

## 4. Exact deletion candidates for PR-1

### 4.1 `narrative_binding.py`

Delete:

- `CORE_STORY_SECTIONS`
- `render_identity_v26(...)`

Delete now-unused imports if they become dead after that removal:

- `build_claim`
- `default_phrase_map_config`

Potentially also delete other imports only if they are proven dead by the
same PR diff. Do not opportunistically widen beyond import cleanup caused
by the dead-truly removal.

Rule:

- final dead-import set is determined by a post-deletion grep / usage
  check, not by import name alone

### 4.2 `narrative_renderer_v26.py`

Delete:

- earlier shadowed `_build_fragment_index(...)` definition

Delete now-unused imports if they become dead after that removal:

- `dataclass`
- `Iterable`

Important:

The later `_build_fragment_index(...)` that had already been migrated into
the canonical `core_story/renderer.py` must not be confused with the dead
earlier one.

## 5. Stale test fix strategy

S2.1.5 found:

- `tests/engine/test_narrative_binding.py`
- `tests/engine/test_narrative_voice_invariants.py`

still import removed `build_narrative`.

PR-1 must choose one of these two approaches and state it explicitly in
the implementation request:

### Preferred

Remove or rewrite the stale tests so they no longer import deleted legacy
symbols.

Reason:

- these are non-canonical root-level tests
- they are already out of sync with the post-S2.2 / post-S2.1.4 state
- leaving them behind will create import-time failure risk later

Decision rule:

- implementer reads both files first:
  - `tests/engine/test_narrative_binding.py`
  - `tests/engine/test_narrative_voice_invariants.py`
- if a file is 100% centered on deleted `build_narrative`, delete the
  file entirely
- if mixed, remove only the dead `build_narrative`-dependent parts and
  keep any unrelated still-valid coverage

### Not preferred

Reintroduce compatibility shims just to satisfy stale tests.

Reason:

- that would undo cleanup and widen legacy burden

## 6. Public contract preservation plan

PR-1 must preserve:

- `response["core_story"]`
- `response["core_story_plan"]`
- `PublicNatalView.core_story`
- `profile_v8.identity_axis_body` fallback
- `core_story_ui`
- mobile / Chart Lab behavior

This should be straightforward because PR-1 does not touch the live
canonical package or route.

## 7. Regression set

Required regression set for PR-1:

- compile checks on touched files
- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_composed_detail_renderer.py`
- directly run the repaired `tests/engine/*` targets if they remain as
  executable tests after the fix

## 8. Risk notes

### Risk 1 — accidental expansion into locally-residue-only cleanup

PR-1 must not delete `_SafeDict`, `normalize_text`, `CORE_STORY_SLOT_ORDER`,
`SLOT_CONNECTORS`, `CONNECTOR_TOKENS`, or any same-file helper cluster
still classified as locally-residue-only.

Mitigation:

- delete only the exact dead-truly list

### Risk 2 — shadowed duplicate confusion

There are two `_build_fragment_index(...)` histories in play:

- dead earlier residue in old `narrative_renderer_v26.py`
- live migrated implementation in `backend/app/natal/narrative/core_story/renderer.py`

Mitigation:

- delete only the old earlier residue definition in the former V26 file

### Risk 3 — stale tests blur the scope

The root-level `tests/engine/*` files are not canonical runtime tests, but
they are still repo artifacts.

Mitigation:

- treat them as explicit scope for PR-1
- fix or remove their stale import dependency as part of the same bounded
  cleanup

## 9. Expected outcome

If PR-1 passes:

- dead-truly residue is reduced
- stale non-canonical legacy test imports are removed
- runtime remains unchanged
- the next cleanup step can focus on one locally-residue-only file cluster
  at a time

## 10. Follow-up sequence after PR-1

Recommended phased order:

1. **PR-1** — dead-truly residue + dead imports + stale `tests/engine/*`
   fix
2. **PR-2** — `narrative_binding.py` locally-residue-only cleanup
3. **PR-3** — `narrative_renderer_v26.py` locally-residue-only cleanup

Each PR keeps the same regression set:

- `backend/tests/test_natal_public_builder.py`
- `backend/tests/test_composed_detail_renderer.py`

## Final recommendation

Proceed with a **narrow PR-1 cleanup**:

- dead-truly only
- dead imports only
- stale `tests/engine/*` legacy import fix

Do not touch the large locally-residue-only clusters yet.
