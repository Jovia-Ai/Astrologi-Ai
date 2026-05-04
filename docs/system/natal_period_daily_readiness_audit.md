# Natal → Period → Daily Readiness Audit

Date: 2026-05-03  
Scope: current backend architecture readiness across natal, period, daily  
Goal: decide whether Daily work is starting too early, or whether Natal and Period are sufficiently ready as foundation

## Executive Answer

Short answer:

```text
Natal foundation: strong enough to support downstream work, but not yet product-render clean.
Period reasoning foundation: ready.
Period renderer/voice: not fully ready, but close enough that period-only validation should happen now.
Daily: too early for major product investment beyond foundation wiring.
```

Go / no-go:

```text
NO-GO for broad Daily voice/product work right now.
GO for period validation and period renderer migration first.
```

Daily should not become the main investment track until period validation completes and period renderer voice migration lands.

---

## 1. Natal Readiness

### What exists

- `CanonicalNatalStateV1` exists in [contracts.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/contracts.py:231).
- `promise hierarchy` exists via [promise_hierarchy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/promise_hierarchy.py) and is used in [state_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/state_builder.py:23).
- `contradiction hierarchy` exists via [contradiction_hierarchy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/contradiction_hierarchy.py) and is used in [state_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/state_builder.py:24).
- `chart_spine` exists in the canonical contract and is reduced from `master_selector` in [state_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/state_builder.py:26).
- `meaning_graph` exists and is built by [meaning_graph.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/meaning_graph.py:112).
- `activation_hooks` exist inside the canonical natal meaning graph in [meaning_graph.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/meaning_graph.py:194).
- Canonical natal renderers exist:
  - [compact_profile_renderer.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/rendering/compact_profile_renderer.py:154)
  - [section_profile_renderer.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/astro_os/natal/rendering/section_profile_renderer.py:75)
- Internal canonical natal endpoints exist:
  - [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:272)
  - [natal_interpretation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/natal_interpretation.py:281)

### What is still legacy

- Main natal product rendering still flows through:
  - [profile_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/profile_narrative_engine.py:139)
  - [public_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:53)
  - `profile_v8`
  - `meaning_graph_v1_1`
  - `profile_v8_projection_v1`
- The runtime registry already marks `profile_narrative_engine.py` as `legacy_compat`; see [voice_runtime_registry.yml](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/voice_runtime_registry.yml:88).
- `master_selector.py` is live and meaning-bearing, but still sits in a mixed world with legacy renderers; see [master_selector.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/narrative/master_selector.py:580).

### Mobile still using legacy branches?

Effectively yes.

There is no separate backend mobile renderer path here; mobile/public consumers are still fed by [build_public_natal_view(...)](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/natal/public_builder.py:53), and that payload still includes legacy-era branches:

- `profile_narrative`
- `profile_v8`
- `meaning_graph`
- `meaning_graph_v1_1`
- `profile_v8_projection_v1`

So even if canonical natal state exists, the product-facing natal surface is not yet canonical-first.

### Synastry/composite using canonical natal state?

Not meaningfully.

- Transit uses canonical natal state for activation context; see [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2415) and [canonical_natal_activation.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/canonical_natal_activation.py:107).
- Synastry still centers `natal_graph_v2` and synastry-specific engines, not `CanonicalNatalStateV1`; see [synastry_analysis.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/services/synastry_analysis.py:6).
- Composite guidance still uses composite structural metadata, not canonical natal state; see [composite_guidance.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/builders/composite_guidance.py:8).

### Natal classification

| Dimension | Status | Reason |
|---|---|---|
| `foundation_ready` | `yes` | Canonical state, promise hierarchy, contradiction hierarchy, chart spine, meaning graph, activation hooks all exist and are wired. |
| `product_render_ready` | `partial` | Canonical renderers exist, but public natal still rides legacy renderers and payload shapers. |
| `downstream_ready` | `partial` | Transit already consumes canonical natal state; synastry/composite do not. |
| `validation_ready` | `partial` | Internal render/state endpoints exist, but no canonical natal product validation pass has closed. |

Natal verdict:

```text
Natal is foundation-ready, but not product-render-ready.
```

---

## 2. Period Readiness

### What exists

- `canonical_period_spine` is live in the transit route and period core flow; see [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2474) and current sample artifacts.
- `period_voice_policy` exists and is canonical authority; see [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:71).
- `manifestation_context` exists and is deterministic; see [manifestation_context_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/manifestation_context_policy.py:87).
- Period story renderer uses canonical policy/context through [astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/astrolog_narrative_engine.py:571).
- Period renderer debug includes manifestation context and voice policy fields; verified in [test_astrolog_narrative_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/tests/test_astrolog_narrative_engine.py:407).

### What still remains transitional

- Legacy event-card bridge is still live through [deep_archetype_engine.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/deep_archetype_engine.py) and [voice_engine_tr.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/voice_engine_tr.py).
- `text_quality_tr.py` is still deeply embedded and not demoted out of live influence; see [voice_runtime_registry.yml](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/voice_runtime_registry.yml:56).
- The current generated period renderer is architecturally canonical but still prose-misaligned with SHOU voice. That gap is why the handcrafted validation pack was needed.

### Legacy natal_promise fallback remains?

Yes, in controlled form.

The period layer still allows natal backing / reason-line behavior rather than being fully standalone:

- `canonical_backing_node_ids`
- `reason_line_allowed`
- `reason_line_seed`

These live in [period_voice_policy.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/period_voice_policy.py:115) and are appropriate as compatibility support, but they confirm period is not fully independent from natal backing logic yet.

### Period voice vNext alignment status

Reasoning layer: strong.  
Renderer prose layer: incomplete.

What is aligned:

- `meaning_intent`
- `rhetorical_frame`
- `manifestation_context`
- debug trace
- deterministic house scene selection

What is not yet aligned:

- generated prose still drifts into system-explanation voice
- handcrafted pack was required because generated period prose did not yet sound like final SHOU
- current best target voice lives in:
  - [handcrafted_validation_pack.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/handcrafted_validation_pack.md)
  - [handcrafted_validation_answer_key.json](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/handcrafted_validation_answer_key.json)

### Generated vs handcrafted voice gap

This is the main period bottleneck now.

Current state:

```text
canonical chain chooses the right meaning
but renderer still explains the system too often
instead of sounding fully SHOU
```

So the remaining period problem is not core reasoning architecture. It is renderer voice migration.

### Sample validation status

- Generated sample pack became structurally valid after runtime/bootstrap fixes.
- Daily was removed from reviewer pack because daily prose still leaks technical/internal artifacts.
- Period-only validation pack exists and is usable.
- Handcrafted SHOU voice validation pack also exists and passes vNext guardrails.
- Human blind validation was later skipped by voice-lead decision; the active target reference is now [handcrafted_period_validation_v4_final.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/handcrafted_period_validation_v4_final.md:1), while [validation_results_2026_05_xx.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/validation_results_2026_05_xx.md:1) remains only as an archived template.

### Period classification

| Dimension | Status | Reason |
|---|---|---|
| `reasoning_ready` | `yes` | Canonical period spine, voice policy, manifestation context, and canonical renderer chain exist. |
| `renderer_ready` | `partial` | Renderer is live and structured, but prose still needs SHOU migration. |
| `voice_ready` | `partial` | Voice spec exists; generated renderer has not yet converged to handcrafted SHOU target. |
| `validation_ready` | `partial_yes` | Period-only validation can run now, but it should validate handcrafted/target voice rather than treat generated prose as final. |

Period verdict:

```text
Period is sufficiently ready as foundation.
The remaining work is renderer/voice migration, not architecture invention.
```

---

## 3. Daily Readiness

### What exists

- `TodayStoryCandidate` exists and is a real canonical reasoning object; see [today_story_candidate.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/today_story_candidate.py:14).
- `DailyTriggerSelection` exists in practice as [daily_selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_selection.py).
- `daily_selection` has already been demoted to selector status in the runtime registry; see [voice_runtime_registry.yml](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/voice_runtime_registry.yml:40).
- `daily_synthesis` is still live in the route and assembles public payload; see [transits.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/api/routes/transits.py:2566).
- `daily_humanizer_tr.py` is still live and imported by `daily_selection.py`; see [daily_selection.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/transit/narrative/daily_selection.py:9).

### What is missing or not yet canonical

- `daily_synthesis` is still a mixed owner, not a pure renderer.
  - Registry status: `renderer_assembler_and_partial_meaning_writer`
  - Evidence: [voice_runtime_registry.yml](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/voice_runtime_registry.yml:46)
- `today_delta_signal` does not currently exist as a runtime field or canonical object.
  - Code search found no runtime implementation under `backend/app`.
  - It exists in spec/tests language only; see [SHOU_VOICE_VNEXT.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/voice/SHOU_VOICE_VNEXT.md:173).
- `manifestation_context` is not yet a first-class daily render input.
  - `TodayStoryCandidate` reuses period voice policy, but does not expose a dedicated daily manifestation-context contract at top level.
  - Current daily scene behavior is still mixed between selection/runtime prose and sample/mock scaffolding.
- A true `daily canonical renderer` does not exist yet.
  - The planned destination is still future `PR-7`.

### Daily classification

| Dimension | Status | Reason |
|---|---|---|
| `reasoning_ready` | `partial_yes` | TodayStoryCandidate exists and demotion of daily_selection is conceptually correct. |
| `renderer_ready` | `no` | daily_synthesis still writes meaning-bearing prose; no pure canonical daily renderer exists. |
| `voice_ready` | `no` | Daily still leaks technical/internal phrasing and is not vNext-clean. |
| `product_ready` | `no` | today_delta_signal missing, manifestation_context not canonically consumed, renderer still mixed. |

Daily verdict:

```text
Daily is not ready for major voice/product expansion.
```

---

## 4. Current Risk

### Are we over-investing in Daily while Natal/Period are not validated?

Yes, if Daily becomes the main migration track now.

More precise answer:

- Natal does not block Daily at the reasoning-foundation level.
- Period is the immediate validation bottleneck.
- Daily still has too many missing canonical pieces to justify front-loading major product effort before period validation closes.

So the risk is not:

```text
Natal is too weak, therefore Daily must stop.
```

The real risk is:

```text
Period is close enough to validate now,
but Daily still lacks core canonical rendering pieces.
Starting big Daily work before closing Period validation risks building on an unproven renderer voice layer.
```

### Which layer is the bottleneck?

Primary bottleneck:

```text
renderer voice layer
```

Across the stack:

- Natal bottleneck: product render/public surface still legacy-heavy
- Period bottleneck: generated renderer prose has not converged to SHOU voice
- Daily bottleneck: renderer architecture is still mixed and missing today-delta contract

### Should Daily work pause until Period validation completes?

For broad Daily voice/product work: yes.  
For minimal foundation prep: no.

Meaning:

- okay:
  - low-risk plumbing
  - audit/alignment work
  - keeping registries/spec/tests coherent
- not okay yet:
  - major Daily renderer migration
  - treating Daily as the proof surface for SHOU vNext

### Should natal renderer be cleaned before daily renderer?

No.

Recommended priority is:

```text
period renderer before natal renderer
```

Reason:

- Period is already the cleanest canonical reasoning surface
- Period validation is closest to decision-grade
- Daily depends more directly on period voice quality than on natal renderer cleanup
- Natal renderer migration is important, but not the critical blocker for the current transit voice roadmap

---

## 5. Recommended Order

Safe next sequence:

1. `handcrafted period validation`
2. `period renderer migration`
3. `daily today-ness signal`
4. `daily canonical renderer`
5. `natal renderer validation`
6. `timing/opportunity engine`

### Why this order

#### 1. Handcrafted period validation

This is the fastest way to validate full SHOU voice direction, not just canonical structure.

#### 2. Period renderer migration

Once handcrafted period voice wins or meaningfully teaches, generated renderer should converge toward that target.

#### 3. Daily today-ness signal

Daily should not expand before it can answer:

```text
Why today?
```

This is the missing canonical daily contract.

#### 4. Daily canonical renderer

Only after today-ness and scene usage are explicit should `daily_synthesis` be reduced to pure rendering or replaced.

#### 5. Natal renderer validation

Natal foundation is solid enough to wait. Its public renderer still needs cleanup, but it is not the next bottleneck in the transit voice migration.

#### 6. Timing/opportunity engine

This is an expansion layer, not a prerequisite for closing the core SHOU voice foundation.

---

## Final Classification Summary

| Layer | Foundation / Reasoning | Renderer | Voice | Validation / Product |
|---|---|---|---|---|
| Natal | `ready` | `partial` | `partial` | `partial` |
| Period | `ready` | `partial` | `partial` | `ready_for_period_only_validation` |
| Daily | `partial` | `not_ready` | `not_ready` | `not_ready` |

---

## Final Go / No-Go

```text
GO: continue foundation work through handcrafted period validation and period renderer migration.
NO-GO: do not continue broad Daily voice/product work as the main track yet.
```

Recommended operating rule:

```text
Daily can receive only minimal prerequisite work until Period validation completes.
Period is the current proof surface.
Natal cleanup should follow, not lead, the current transit voice migration.
```
