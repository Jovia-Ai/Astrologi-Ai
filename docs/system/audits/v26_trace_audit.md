# V26 Trace Audit

## Scope

This is an audit-only artifact for the V26 narrative stack.

No code changes.
No runtime changes.
No deletes.
No refactor.

Target stack:

- `backend/app/builders/narrative_binding.py`
- `backend/app/builders/narrative_renderer_v26.py`
- `backend/app/style/style_pack_v26_tr.py`
- `build_narrative`
- `build_core_story_plan`
- `build_domain_narrative_v26`
- `render_core_story`
- `StylePackV26TR`

## Executive Verdict

The V26 stack is **not fully dead**.

Current state splits into two parts:

1. **Live canonical natal path**
   - `build_core_story_plan(...)`
   - `render_core_story(...)`
   - reachable from canonical natal endpoints

2. **Currently caller-less / effectively dead subpath**
   - `build_narrative(...)`
   - `build_domain_narrative_v26(...)`
   - `StylePackV26TR`

So the whole stack is **not DELETE-safe** as one unit.

Overall recommendation:

- **MIGRATE-callers-first**

Reason:

- a public canonical natal endpoint still reaches the `core_story` half of the V26 stack
- deleting or freezing the whole unit blindly would risk current natal public behavior
- only the `build_narrative -> build_domain_narrative_v26 -> StylePackV26TR` branch currently looks unused

## Caller Table

| Symbol / File | Direct caller | Classification | Evidence |
|---|---|---|---|
| `build_core_story_plan(...)` | `backend/app/api/routes/natal_interpretation.py` | `runtime canonical path` | [natal_interpretation.py:2581](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2581) |
| `render_core_story(...)` | `backend/app/api/routes/natal_interpretation.py` | `runtime canonical path` | [natal_interpretation.py:2589](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2589) |
| `build_narrative(...)` | no callsites found; imported in natal route only | `dead / unused` | import at [natal_interpretation.py:29](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:29), no callsites in repo search |
| `build_domain_narrative_v26(...)` | only called by `build_narrative(...)` | `dead / unused` | [narrative_binding.py:54](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:54) plus no external callsites |
| `StylePackV26TR` | instantiated by `build_domain_narrative_v26(...)`; imported in `narrative_binding.py` | `dead / unused` in canonical chains | [narrative_renderer_v26.py:27](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:27), [narrative_binding.py:17](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:17) |
| `backend/app/builders/narrative_binding.py` | imported by natal route | `mixed: partial live, partial dead` | [natal_interpretation.py:29](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:29) |
| `backend/app/builders/narrative_renderer_v26.py` | imported by natal route for `render_core_story`; imported by `narrative_binding.py` for `build_domain_narrative_v26` | `mixed: partial live, partial dead` | [natal_interpretation.py:30](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:30), [narrative_binding.py:14](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:14) |
| `backend/app/style/style_pack_v26_tr.py` | imported by `narrative_renderer_v26.py` and `narrative_binding.py` only | `dead / unused` in current public chains | [narrative_renderer_v26.py:10](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:10), [narrative_binding.py:17](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:17) |

## Call Chain Evidence

### A. Live canonical natal chain

Canonical natal endpoints:

- `/interpret`  
  [backend/app/api/routes/natal_interpretation.py:1215](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1215)
- `/interpret/ui`  
  [backend/app/api/routes/natal_interpretation.py:1279](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1279)
- `/interpret/premium`  
  [backend/app/api/routes/natal_interpretation.py:1503](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1503)
- `/interpret/premium/ui`  
  [backend/app/api/routes/natal_interpretation.py:1526](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1526)

In the shared natal finalize path:

1. `response["core_story_plan"] = build_core_story_plan(...)`  
   [backend/app/api/routes/natal_interpretation.py:2581](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2581)
2. `response["core_story"] = render_core_story(...)`  
   [backend/app/api/routes/natal_interpretation.py:2589](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2589)
3. `build_public_natal_view(...)` reads `response["core_story"]` and emits it into public payload  
   [backend/app/natal/public_builder.py:83](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:83), [backend/app/natal/public_builder.py:187](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:187)

Conclusion:

- `build_core_story_plan(...)` and `render_core_story(...)` are on the live canonical natal path
- V26 is therefore still partly runtime-relevant

### B. Dead-looking subpath

`build_narrative(...)` exists here:

- [backend/app/builders/narrative_binding.py:20](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:20)

Inside it:

- `build_domain_narrative_v26(...)` is called here  
  [backend/app/builders/narrative_binding.py:54](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_binding.py:54)

Inside `build_domain_narrative_v26(...)`:

- `StylePackV26TR()` is instantiated here  
  [backend/app/builders/narrative_renderer_v26.py:27](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/narrative_renderer_v26.py:27)

Repo-wide caller search result:

- `build_narrative(...)` has no callsites beyond its own definition
- `build_domain_narrative_v26(...)` has no callsites beyond `build_narrative(...)`
- `StylePackV26TR` has no runtime callsites beyond `build_domain_narrative_v26(...)`

Conclusion:

- this branch currently appears unused
- it is not on current canonical natal/synastry/transit public paths

## Can Any Public Endpoint Reach V26?

### Yes: canonical natal can reach part of it

Reachable:

- `build_core_story_plan(...)`
- `render_core_story(...)`

Through:

- natal `/interpret`
- natal `/interpret/ui`
- natal premium variants that share the same finalize path

Evidence:

- route definitions at [natal_interpretation.py:1215](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1215), [natal_interpretation.py:1279](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1279), [natal_interpretation.py:1503](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1503), [natal_interpretation.py:1526](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:1526)
- finalize path at [natal_interpretation.py:2581](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:2581)

### No evidence: synastry or transit public endpoints reaching V26

Repo search over `backend/app/transit` and `backend/app/synastry` for:

- `narrative_binding`
- `narrative_renderer_v26`
- `StylePackV26TR`
- `build_narrative(...)`
- `build_core_story_plan(...)`
- `build_domain_narrative_v26(...)`
- `render_core_story(...)`

returned no matches.

Transit public builder currently routes through:

- `composer.py`
- `deep_archetype_engine.py`
- `text_quality_tr.py`
- `public_voice_en.py`
- `public_builder.py`

Evidence:

- [backend/app/transit/present/public_builder.py:1](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/present/public_builder.py:1)

Synastry public builder currently routes through:

- `synastry public builder`
- overlay/aspect formatting
- synastry narrative/router layers

Evidence:

- [backend/app/synastry/public_builder.py:1](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/synastry/public_builder.py:1)

Conclusion:

- current transit public builders cannot reach V26
- current synastry public builders cannot reach V26

## Per-File Classification

### `backend/app/builders/narrative_binding.py`

Classification:

- `mixed`

Why:

- `build_core_story_plan(...)` is live
- `build_narrative(...)` appears unused

### `backend/app/builders/narrative_renderer_v26.py`

Classification:

- `mixed`

Why:

- `render_core_story(...)` is live
- `build_domain_narrative_v26(...)` appears unused

### `backend/app/style/style_pack_v26_tr.py`

Classification:

- `dead / unused` in current canonical chains

Why:

- only reachable through `build_domain_narrative_v26(...)`
- that branch currently has no callers

## Test-Only / Debug-Only / Artifact-Only Findings

Search over `backend/tests` found no direct test callers for:

- `build_narrative(...)`
- `build_core_story_plan(...)`
- `build_domain_narrative_v26(...)`
- `render_core_story(...)`
- `StylePackV26TR`

So current classification is:

- not `test only`
- not `debug / artifact only`
- instead: `runtime canonical` for the core-story branch, `dead / unused` for the domain narrative branch

## Recommendation

### Recommendation: `MIGRATE-callers-first`

Reasoning:

- A live canonical natal path still depends on part of the V26 stack.
- The stack is internally split:
  - core-story branch is live
  - domain-narrative/style-pack branch appears unused
- Deleting or freezing the whole unit would mix a real runtime dependency with a likely dead branch.

So the safe sequence is:

1. treat `build_core_story_plan + render_core_story` as live runtime
2. separate them conceptually from `build_narrative + build_domain_narrative_v26 + StylePackV26TR`
3. only after that, decide whether the dead-looking branch is delete-safe

## Risk Notes

### Risk 1: false delete from file-level thinking

At file level, `narrative_binding.py` and `narrative_renderer_v26.py` look like one old stack.
At symbol level, they are split:

- some functions are live
- some are not

Deleting by file rather than symbol would be unsafe.

### Risk 2: canonical natal regression

`render_core_story(...)` feeds `response["core_story"]`, and `build_public_natal_view(...)` exposes that in public output.

So removing or freezing it without migration would change public natal behavior.

### Risk 3: unused import can hide future confusion

`build_narrative` is still imported into natal route:

- [backend/app/api/routes/natal_interpretation.py:29](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:29)

but not called.

That means code readers can easily overestimate how alive the full V26 stack is.

## Next Action

Recommended next action:

- run a **split audit**, not a delete pass

Specifically:

1. isolate the **live V26 core-story branch**
   - `build_core_story_plan`
   - `render_core_story`
2. isolate the **dead-looking domain narrative branch**
   - `build_narrative`
   - `build_domain_narrative_v26`
   - `StylePackV26TR`
3. then decide separately:
   - live branch: `freeze-only` or `migrate`
   - dead branch: `delete-safe?` after one final negative-caller verification

## Final Decision

Overall stack recommendation:

- **MIGRATE-callers-first**

Not safe to label the full V26 stack as:

- `DELETE-safe`

because part of it is still on the canonical natal runtime path.
