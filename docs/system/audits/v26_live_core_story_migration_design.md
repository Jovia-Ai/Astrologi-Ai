# S2.1.2 — V26 LIVE Core Story Migration Target Design

## Scope

This is a design-only artifact.

No code.
No runtime change.
No deletion.
No refactor.

This document decides where the **live** V26 `core_story` branch should
eventually migrate or consolidate while preserving the current public
contract.

Out of scope:

- endpoint changes
- public schema changes
- mobile changes
- Chart Lab contract changes
- ARC/A2 merge
- Phase-4 / deep_read work

## 1. Current live branch

The S2.1 trace showed that the V26 stack is split:

- dead branch already removed in S2.2:
  - `build_narrative(...)`
  - `build_domain_narrative_v26(...)`
  - `StylePackV26TR`
- live branch still on canonical natal runtime:
  - `build_core_story_plan(...)`
  - `render_core_story(...)`

Live call chain:

1. canonical natal routes share the same finalize path in
   [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2581)
2. `response["core_story_plan"] = build_core_story_plan(...)`
3. `response["core_story"] = render_core_story(...)`
4. [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:83)
   reads `response["core_story"]`
5. [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:187)
   emits it into `PublicNatalView.core_story`

Known downstream consumers:

- public payload:
  - [public_models.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_models.py:43)
- `profile_v8` fallback:
  - [profile_v8_payload_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/profile_v8_payload_builder.py:1748)
- `data_quality` debug/summary path from `core_story_plan`:
  - [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2688)
- mobile / Chart Lab readers of `core_story` or `core_story_ui`:
  - [profile_v8_adapter.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_v8_adapter.dart:281)
  - [profile_v9_adapter.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/profile/profile_v9_adapter.dart:272)
  - [chart_lab_page.dart](/Users/sahradenizozdogan/Astrologi-Ai/mobile/lib/app/tabs/chart_lab_page.dart:775)

## 2. Hard invariants

Any migration target must preserve all of the following:

- `response["core_story"]` remains byte-compatible unless explicitly
  approved otherwise
- `response["core_story_plan"]` schema remains compatible with downstream
  `build_core_story_ui` and `data_quality` consumers
- mobile and Chart Lab must not break
- no endpoint changes
- no public schema changes
- no ARC/A2 merge
- no Phase-4 / deep_read coupling

Practical reading:

- this is not a wording redesign problem
- this is not a renderer-modernization pass
- this is a contract-preserving relocation / consolidation decision

## 3. Option A — Migrate into signature renderer

Target:

- move `build_core_story_plan(...)` and `render_core_story(...)` into the
  `profile_narrative_engine_signature` / signature-renderer family

### Pros

- puts more natal prose under one modern canonical narrative area
- could reduce long-term conceptual duplication between signature
  narrative rendering and `core_story`
- aligns with the broader consolidation direction where
  [profile_narrative_engine_signature.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/profile_narrative_engine_signature.py:1778)
  is already a rescued core renderer

### Risks

- high contract risk: signature renderer is block-oriented and template
  driven; `core_story` is a three-paragraph longform string with its own
  paragraph synthesis rules
- strong coupling risk: `core_story_plan` is currently consumed as a
  plan/debug/data-quality object, not as the same semantic block model
  used by signature narrative
- risk of hidden wording drift even if public schema stays identical
- higher regression probability in mobile / Chart Lab because the current
  `core_story` contract is simpler than signature block structures

### Likely touched files

- `backend/app/natal/narrative/profile_narrative_engine_signature.py`
- `backend/app/api/routes/natal_interpretation.py`
- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`
- possibly `backend/app/natal/public_builder.py` only if import paths or
  guard tests need adjustment

### Public contract preservation plan

- keep `response["core_story_plan"]` key and shape identical
- keep `response["core_story"]` text byte-identical
- preserve `profile_v8.identity_axis_body` fallback behavior unchanged
- preserve `PublicNatalView.core_story` and `core_story_ui` field shape

### Test requirements

- preserve S2.1.1 snapshot tests for:
  - `public["core_story"]`
  - `response["core_story_plan"]`
  - `profile_v8.identity_axis.body` fallback
- add import-path migration tests if implementation later moves symbols
- add exact text equality snapshot for the canonical 1996 Istanbul
  fixture before and after migration

### Rollback strategy

- keep old import path behind a temporary compatibility wrapper
- revert caller wiring in `natal_interpretation.py`
- do not delete old V26-live symbol definitions until snapshot parity is
  proven across fixtures

### Verdict on A

- possible, but too coupled and too regression-prone for the first move

## 4. Option B — Migrate to a dedicated `core_story_module.py`

Target:

- extract the live branch into a dedicated module, for example:
  - `backend/app/natal/narrative/core_story_module.py`
  - or adjacent natal narrative location with explicit ownership

This option moves the symbols out of V26/legacy-named files without
forcing them into the signature renderer.

### Pros

- best separation of concerns
- removes misleading V26/legacy naming from a still-live canonical path
- preserves current `core_story` architecture as its own contract-bearing
  module
- easiest place to keep plan + renderer together while their downstream
  consumers remain stable
- lowers future deletion risk because the dead branch and live branch stop
  cohabiting legacy-branded files

### Risks

- still requires careful symbol relocation because `build_core_story_plan`
  and `render_core_story` are both live and both contract-sensitive
- modest duplication remains with signature narrative concepts
- if implemented sloppily, import churn could be mistaken for a semantic
  rewrite

### Likely touched files

- new module:
  - `backend/app/natal/narrative/core_story_module.py`
- caller rewiring:
  - `backend/app/api/routes/natal_interpretation.py`
- compatibility shims or wrappers:
  - `backend/app/builders/narrative_binding.py`
  - `backend/app/builders/narrative_renderer_v26.py`
- tests:
  - `backend/tests/test_natal_public_builder.py`
  - any dedicated route-level regression tests covering `core_story_plan`

### Public contract preservation plan

- preserve exact keys:
  - `response["core_story_plan"]`
  - `response["core_story"]`
- preserve exact `core_story_plan` schema, especially:
  - `schema_version`
  - `plan_id`
  - `sections`
  - `upper_meaning`
  - `data_quality`
  - `debug`
- preserve `public["core_story"]` bytes and paragraph boundaries
- preserve `profile_v8.identity_axis_body` fallback behavior
- preserve mobile/Chart Lab read paths with no payload changes

### Test requirements

- keep S2.1.1 snapshot coverage as migration safety net
- add route-level parity tests for:
  - `/interpret/ui`
  - debug `data_quality` detail derived from `core_story_plan`
- add negative test that migration does not change public field set
- add import-compat tests if old locations remain wrappers temporarily

### Rollback strategy

- keep legacy import wrappers during the first migration step
- caller switch can be reverted in one place:
  - `natal_interpretation.py`
- if parity fails, old live functions remain callable until the wrapper is
  removed in a later cleanup step

### Verdict on B

- strongest first migration target
- minimizes naming debt without coupling `core_story` to the signature
  renderer too early

## 5. Option C — Rescue as-is and only rename/split from V26 legacy naming

Target:

- keep behavior where it is for now
- formally classify the live branch as rescued canonical code
- optionally do only a naming/documentation split later

### Pros

- lowest immediate regression risk
- no conceptual or structural coupling added
- acknowledges that the live branch is real production behavior and not
  dead legacy
- cheapest path if current priority is only to stop accidental deletion

### Risks

- leaves a misleading file/module story in place:
  - live canonical logic still appears to live in legacy/V26 files
- keeps mixed ownership:
  - one file pair looks “legacy” but contains current canonical runtime
- future cleanup remains harder because dead/live boundaries stay blurred
- does not reduce architectural confusion for later maintainers

### Likely touched files

- none immediately for design-only outcome
- later documentation-only or light wrapper work might touch:
  - `backend/app/builders/narrative_binding.py`
  - `backend/app/builders/narrative_renderer_v26.py`

### Public contract preservation plan

- simplest of all options:
  - do not move anything
  - preserve current payload and caller graph exactly

### Test requirements

- current S2.1.1 snapshot safety net remains mandatory
- no new behavior tests required unless a later rename/split is attempted

### Rollback strategy

- trivial: no migration means no migration rollback

### Verdict on C

- safest short-term holding pattern
- not a real consolidation outcome

## 6. Option comparison

| Option | Contract risk | Naming debt reduction | Architectural clarity | Migration effort | Recommendation status |
|---|---|---:|---:|---:|---|
| A) signature renderer | High | High | Medium | High | Not first choice |
| B) dedicated core story module | Medium-low | High | High | Medium | Best target |
| C) rescue as-is | Low | Low | Low-medium | Low | Acceptable defer/hold |

## 7. Public contract preservation strategy

Regardless of target, the migration must be staged as contract
preservation, not modernization.

Required preservation points:

1. `response["core_story"]`
   - exact string equality
   - exact paragraph count/boundaries
2. `response["core_story_plan"]`
   - exact key compatibility for debug/data-quality readers
3. `public["core_story"]`
   - exact output after public builder humanization path
4. `profile_v8.identity_axis_body`
   - same fallback semantics from `core_story_ui.text` or `core_story`
5. mobile / Chart Lab
   - no payload or field-shape drift

## 8. Test gate before any future implementation

Before any S2.1.3 code move:

- S2.1.1 snapshot suite stays green
- exact `public["core_story"]` parity for canonical natal fixture
- exact `response["core_story_plan"]` schema parity
- no public field-set drift in `/interpret/ui`
- no regression in `profile_v8.identity_axis.body`
- no mobile/Chart Lab contract drift

## 9. Recommendation

Recommended target:

- **migrate to dedicated core_story module**

Why:

- it preserves the live `core_story` contract as its own canonical unit
  without forcing premature integration into the signature renderer
- it removes misleading V26 legacy naming from a live public-runtime path
- it gives the cleanest caller-preserving path from S2.1.1 safety net to a
  later S2.1.3 implementation step

Not recommended as first move:

- migrate to signature renderer

Acceptable only as short-term hold:

- rescue as-is

## Final recommendation

**migrate to dedicated core_story module**
