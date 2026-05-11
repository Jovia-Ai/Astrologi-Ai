# Natal Canonical Core Migration Plan

Date: 2026-05-02
Scope: Natal-only migration roadmap from current multi-branch meaning system to one canonical natal core.
Goal: Stop treating natal as many overlapping narrative authorities and turn it into one canonical state model that all future surfaces and future transit/period/synastry logic can consume.

## Executive Decision

This is the right direction:

1. Natal Canonical Core
2. Period
3. Daily
4. Synastry / Composite

The key architectural decision is:

Do not rewrite natal from zero.
Consolidate the existing real natal intelligence into one canonical state.

That means:

- preserve the strong reasoning substrate
- demote branch-specific narrative authorities
- build one internal natal state contract first
- render from that state later

## Core Principle

The migration target is not:

- better copy
- cleaner profile payloads
- nicer renderer structure

The migration target is:

one sovereign natal meaning core

Invariant rules:

- No evidence, no claim.
- No node_id, no render.
- No trace, no primary hierarchy.

Everything else becomes one of:

- source calculator
- structural feature extractor
- canonical reasoner
- renderer
- legacy surface

## Why Natal First

Transit, daily, period, synastry, and composite all ultimately depend on natal answers:

- What is promised in the chart?
- What is central in the character architecture?
- What is compensation vs essence?
- What is a core contradiction vs a secondary one?
- What line of the chart is currently being activated?

Without a canonical natal core, every later system remains branchy and unstable.

## What Stays Strong

These are the modules to preserve and build around:

- `backend/app/natal/dispositor_engine.py`
- `backend/app/natal/natal_graph_v2.py`
- `backend/app/natal/promise_vector_engine.py`
- `backend/app/natal/narrative/natal_feature_graph.py`
- `backend/app/natal/narrative/contradiction_engine.py`
- `backend/app/natal/narrative/master_selector.py`

These are not legacy baggage.
These are the nearest things to the true natal cognition core.

## What Gets Demoted

These should stop behaving like primary meaning authorities:

- `sections_v2`
- `supporting_threads`
- `personality_imprint`
- `profile_narrative`
- `profile_v8`
- `full_map_v8`
- `backend/app/natal/public_builder.py` in old branch-coordinator mode
- downstream graph extraction from already-written narrative branches
- frontend semantic merging across natal branches

They do not need to be deleted immediately.
But they should be reclassified as:

- legacy surfaces
- renderer inspiration
- comparison artifacts
- compatibility layers

## Phase Plan

## Phase 0: Constraint Reset

Because the app is not live and there are no users, optimize for semantic correctness over backward compatibility.

Rules for this migration:

- new natal features should not be added to old branch authorities
- backward compatibility is optional, not primary
- debug visibility is more important than public polish
- state correctness comes before rendering quality

## Phase 1: Natal Ontology Decision Sheet

### Goal

Define the minimum natal ontology before coding the core.

### Decisions to lock

- promise domain list
- character pattern type list
- contradiction type list
- evidence role list
- chart spine fields
- v1 technical scope
- user-facing technical evidence density
- legacy branch mapping policy

### Recommended output

Create a decision artifact such as:

- `docs/system/natal_ontology_decision_sheet.md`

### Constraint

Do not let this phase sprawl.
Maximum target: 8 to 10 decisions.

### Important guidance

Do not finalize taxonomy in the abstract only.
Validate each category against real charts.
The ontology should survive contact with actual runtime examples.

### Acceptance rule

This phase cannot be marked complete until it is validated against at least 15 golden charts.

Additional minimum acceptance:

- each promise domain must have at least 2 chart-backed examples or be marked `v1_experimental`
- each contradiction type must have at least 1 chart-backed example or be excluded from `v1`
- each evidence role must have at least 1 concrete chart example

## Phase 2: Semantic Registry

### Goal

Inventory where natal meaning is currently produced.

### Output

Create:

- `backend/app/astro_os/natal/natal_semantic_registry.yml`

### For each important file, record

- current role
- semantic authority level
- keep / refactor / demote / delete status
- new role
- reason

### Example role taxonomy

- `SOURCE_CALCULATOR`
- `STRUCTURAL_FEATURE_EXTRACTOR`
- `CANONICAL_REASONER`
- `RENDERER`
- `LEGACY_SURFACE`
- `DELETE_CANDIDATE`

### Recommended classification

`SOURCE_CALCULATOR`

- `backend/app/natal/dispositor_engine.py`
- chart normalization / extraction helpers

`STRUCTURAL_FEATURE_EXTRACTOR`

- `backend/app/natal/natal_graph_v2.py`
- `backend/app/natal/promise_vector_engine.py`
- `backend/app/natal/narrative/natal_feature_graph.py`
- `backend/app/natal/narrative/contradiction_engine.py`

`CANONICAL_REASONER`

- new `backend/app/astro_os/natal/state_builder.py`
- refactored `master_selector` output reducer

`RENDERER`

- future `profile_renderer.py`
- future `compact_renderer.py`

`LEGACY_SURFACE`

- `sections_v2`
- `supporting_threads`
- `personality_imprint`
- `profile_narrative`
- `profile_v8`
- `full_map_v8`
- `public_builder.py` in its old branch-coordinator role

## Phase 3: Canonical Contract

### Goal

Define one internal source of natal meaning truth.

### New directory

- `backend/app/astro_os/natal/`

### Initial files

- `contracts.py`
- `evidence.py`
- `legacy_adapter.py`
- `state_builder.py`

### Required first contract

- `CanonicalNatalStateV1`

### Minimum model families

- `NatalEvidence`
- `NatalPromiseNode`
- `CharacterPatternNode`
- `ContradictionNode`
- `ChartSpine`
- `CanonicalNatalStateV1`

### Required internal node families

These do not need to be public-facing render nodes, but they must exist in the canonical contract or its internal structural layer:

- `PlanetConditionNode`
- `DispositorRouteNode`
- `HouseRulerRouteNode`
- `AspectPatternNode`

### First success criterion

Not beautiful text.
Not final user payload.

First success means:

- one promise hierarchy
- one contradiction hierarchy
- one chart spine

### Definition of Done

- `contracts.py` type-checks cleanly
- an empty-but-valid `CanonicalNatalStateV1` can be instantiated
- every public claim-capable model requires `evidence[]`
- `ChartSpine` has a stable empty shape even before population

## Phase 4: Golden Chart Corpus

### Goal

Prevent the migration from becoming theory-only.

### Output

Create a fixed natal corpus, for example:

- `backend/tests/golden/natal_canonical_core/`

Each chart should define expectations like:

- core or major promises
- primary contradiction
- relational line
- work/visibility line
- expression or regulation pattern

### Test style

Test state, not prose.

### Example expectations

- expected promise domains
- expected central contradictions
- evidence that must appear
- node ids that must be produced

### Definition of Done

- at least 15 golden charts exist
- ontology acceptance checks are wired into the corpus
- each golden chart defines at least one expected promise, contradiction, or spine expectation

## Phase 5: Legacy Adapter

### Goal

Connect current strong natal sources to the new canonical contract without rewriting the whole engine.

### New file

- `backend/app/astro_os/natal/legacy_adapter.py`

### Role

Collect existing structural outputs and normalize them into one bundle for the state builder.

### Recommended bundle shape

- raw chart
- dispositor data
- natal graph v2
- feature graph
- promise vectors
- contradiction signatures
- master selector

### Important rule

This adapter should not generate user-facing meaning.
It only collects and normalizes reasoning inputs.

### Definition of Done

- adapter skeleton returns a valid normalized bundle shape
- bundle fields are source-labeled for traceability
- no renderer-facing prose is emitted from adapter code

## Phase 6: State Builder Skeleton

### Goal

Get the internal state route working early, even if partially filled.

### New file

- `backend/app/astro_os/natal/state_builder.py`

### Output

Build a partial but valid `CanonicalNatalStateV1`.

### First route

- `/internal/astro-os/natal-state/{chart_id}`

or equivalent internal-only route

### First debug requirements

- legacy sources used
- evidence counts
- which source fed which node
- why a contradiction became primary
- why a spine line was selected
- suppressed candidates
- conflicting evidence
- fallback used
- legacy branch overlap
- golden expectation misses

### Recommended debug fields

- `suppressed_candidates`
- `conflicting_evidence`
- `fallback_used`
- `legacy_branch_overlap`
- `golden_expectation_misses`

### Definition of Done

- internal route returns a valid partial state
- debug trace includes both selected and suppressed reasoning artifacts
- node-to-source traceability is present for every populated core node

## Phase 7: Promise Hierarchy

### Goal

Turn existing vector and feature outputs into ranked natal promises.

### New file

- `backend/app/astro_os/natal/promise_hierarchy.py`

### Inputs

- promise vectors
- feature graph
- dispositor routes
- house rulers
- contradiction signatures
- master selector candidates

### Outputs

Promises ranked as:

- `core`
- `major`
- `supporting`
- `minor`

### Recommended constraint

Keep the public canonical state compact:

- max 3 core promises
- max 5 major promises
- max 5 character patterns
- max 3 contradictions

### Governing logic

A promise should rank higher when it is:

- chart-ruler linked
- angular or repeated through multiple evidence routes
- reinforced by dispositors or ruler recursion
- central in contradiction logic
- represented in the chart spine

### Definition of Done

- golden charts produce expected `core` or `major` promises in at least 80 percent of cases
- every `core` promise has at least 2 evidence routes
- no `core` promise is created from a single weak signal
- every `core` promise links to at least one character pattern or contradiction

## Phase 8: Contradiction Hierarchy

### Goal

Make contradictions canonical, not decorative.

### New file

- `backend/app/astro_os/natal/contradiction_hierarchy.py`

### Inputs

- contradiction signatures
- feature graph polarity
- promise hierarchy

### Output

Rank contradictions as:

- `primary`
- `secondary`
- `minor`

### Principle

Contradictions are not side flavor.
They are one of the best ways to identify how a chart actually lives.

### Definition of Done

- every `primary` contradiction has at least 2 polarity evidence routes
- every `primary` contradiction is connected to either chart spine or a `core`/`major` promise
- no contradiction is publishable without `integration_path`

## Phase 9: Chart Spine Reducer

### Goal

Refactor `master_selector` from a semi-independent meaning engine into a spine reducer for canonical state.

### Role change

Old role:

- chart line selector with partial semantic authority

New role:

- canonical state spine reducer

### Recommended spine fields

- `primary_identity_line`
- `emotional_regulation_line`
- `relational_line`
- `work_visibility_line`
- `shadow_protection_line`
- `growth_integration_line`

### Important principle

`master_selector` should not decide truth alone.
It should summarize canonical truth into a stable spine.

Invariant:

- `master_selector` may produce spine candidates only
- a spine candidate cannot be published unless it is backed by at least one `core`/`major` promise or one `primary`/`secondary` contradiction
- selector-only lines without backing must be downgraded or suppressed

### Definition of Done

- every spine line references `node_id`
- `master_selector`-only lines are not publishable
- each published spine line has evidence trace

## Phase 10: Internal Comparison Mode

### Goal

Compare old branch outputs against new canonical state before deletion or public migration.

### Outputs

- comparison snapshots
- mismatch reports
- false-loss detection

### Compare against

- `profile_narrative`
- `personality_imprint`
- `sections_v2`
- `supporting_threads`
- `profile_v8`

### Questions to answer

- Which old branch had unique meaning worth preserving?
- Which branch was only alternate packaging?
- Which phrases are worth rescuing into renderers?
- Which branches can be safely demoted or removed?

## Phase 11: First Renderers

### Goal

Only after state is stable, build renderers from canonical state.

### New directory

- `backend/app/astro_os/natal/rendering/`

### First renderer targets

- `compact_profile_renderer.py`
- `section_profile_renderer.py`

### Principle

Renderers may:

- compress
- sequence
- style
- translate technical evidence lightly

Renderers may not:

- invent new meaning
- override promise hierarchy
- replace contradiction hierarchy
- perform semantic arbitration

### Definition of Done

- renderers consume canonical state only
- every rendered claim maps to `node_id` plus `evidence[]`
- renderer tests fail if a claim is emitted without backing node trace

## Phase 12: Legacy Surface Demotion

### Goal

Move old natal surfaces out of the primary meaning path.

### Policy

Do not necessarily delete immediately.

But mark as:

- legacy compare only
- compatibility only
- renderer inspiration only

### Priority demotions

- `sections_v2`
- `supporting_threads`
- `personality_imprint`
- `profile_narrative`
- `profile_v8`
- `full_map_v8`

## Phase 13: Upstream Natal Meaning Graph

### Goal

Rebuild meaning graph from canonical natal state, not from already-written copy branches.

### New direction

`CanonicalNatalStateV1 -> NatalMeaningGraph`

### Recommended node types

- `natal_promise`
- `character_pattern`
- `contradiction`
- `planet_condition`
- `dispositor_chain`
- `house_ruler_route`
- `aspect_pattern`

### Recommended edge types

- `supports`
- `contradicts`
- `routes_through`
- `governed_by`
- `manifests_in`
- `activates_sensitivity`
- `integrates_through`

### Why this matters

This graph later becomes the source for:

- period activation
- daily activation
- synastry touchpoints
- composite resonance

## Phase 14: Mobile Contract Simplification

### Goal

Stop frontend from merging meaning across multiple natal branches.

### New endpoint direction

- `/v1/natal/state/{chart_id}`
- `/v1/natal/profile/{chart_id}`

### Frontend rule

Frontend consumes:

- canonical state
- renderer output

Frontend does not decide:

- which natal branch is more authoritative
- how to merge profile_v8 vs profile_narrative vs sections

## Delivery Sequence

## Weeks 1-2

- ontology decision sheet
- semantic registry
- contracts
- golden chart set
- legacy adapter skeleton

## Weeks 3-4

- state builder skeleton
- internal natal state endpoint
- promise hierarchy
- contradiction hierarchy

## Weeks 5-6

- chart spine reducer
- internal old vs new comparison
- canonical debug trace
- first state validity tests

## Weeks 7-8

- first renderer set
- upstream natal meaning graph
- legacy surface demotion
- frontend contract simplification prep

## PR-Based Delivery Plan

### PR-1 Foundation

- `docs/system/natal_ontology_decision_sheet.md`
- `backend/app/astro_os/natal/contracts.py`
- `backend/app/astro_os/natal/natal_semantic_registry.yml`
- `backend/tests/golden/natal_canonical_core/`
- `backend/app/astro_os/natal/legacy_adapter.py` skeleton

### PR-2 State Skeleton

- `backend/app/astro_os/natal/state_builder.py`
- internal natal-state route
- debug trace v0
- empty or partial state tests

### PR-3 Promise Hierarchy

- `backend/app/astro_os/natal/promise_hierarchy.py`
- promise ranking
- evidence mapping
- golden promise tests

### PR-4 Contradiction and Spine

- `backend/app/astro_os/natal/contradiction_hierarchy.py`
- chart spine reducer
- `master_selector` demotion tests
- golden spine tests

### PR-5 Comparison Mode

- old vs new semantic snapshots
- phrase rescue list
- legacy loss report

### PR-6 Renderers

- `compact_profile_renderer.py`
- `section_profile_renderer.py`
- no-claim-without-evidence render tests

### PR-7 Upstream Graph

- `NatalMeaningGraph` from `CanonicalNatalState`
- node and edge contracts
- transit-ready activation hooks

## Success Criteria

## Minimum success

For one chart, the system can produce:

- one valid canonical natal state
- one promise hierarchy
- one contradiction hierarchy
- one chart spine
- evidence trace for every major claim

## Strong success

For a stable golden chart set, the system shows:

- cross-chart consistency
- no major claim without evidence
- renderer outputs consistent with canonical state
- old branches no longer needed for meaning authority

## Test Strategy

### 1. Golden state tests

Assert:

- promise presence
- contradiction ranking
- spine line selection
- evidence inclusion

### 2. No-claim-without-evidence tests

Every rendered claim should link to:

- node id
- evidence entries

### 3. Cross-render consistency tests

For the same canonical state:

- compact renderer
- section renderer
- future story renderer

must preserve the same core promises and contradictions.

### 4. Legacy comparison tests

Use old branches only to detect:

- semantic loss
- phrase rescue opportunities
- missing domains

## Risks

## Risk 1: Ontology phase becomes endless

Mitigation:

- limit to 8 to 10 decisions
- validate decisions against real charts immediately

## Risk 2: Renderer work starts too early

Mitigation:

- do not prioritize copy before state
- enforce `state -> graph -> renderer`

## Risk 3: Old branches are deleted before value extraction

Mitigation:

- demote first
- compare second
- remove last

## Risk 4: `master_selector` becomes the new hidden authority

Mitigation:

- keep selector downstream of promise + contradiction logic
- use it as a spine reducer, not sole truth engine

## Risk 5: The canonical state becomes too large and noisy

Mitigation:

- strict ranking limits
- compact public state
- richer debug only in internal mode

## Final Recommendation

Proceed with this migration.

The direction is sound.
The app is not live.
The natal substrate is already strong enough to justify an aggressive consolidation.

The order should be:

1. ontology
2. contract
3. semantic registry
4. legacy adapter
5. state builder
6. promise hierarchy
7. contradiction hierarchy
8. spine reducer
9. internal endpoint
10. renderer
11. legacy demotion

If this is done correctly, natal stops being:

"many smart branches about the same chart"

and becomes:

"one canonical astrologic natal mind that every other system can trust."
