# Natal Ontology Decision Sheet

Date: 2026-05-02
Status: draft_for_pr1_foundation
Scope: Canonical natal core ontology decisions that must be stable before higher-order state building and renderer migration.

## Purpose

This sheet defines the first bounded ontology for `CanonicalNatalStateV1`.
It is intentionally smaller than the eventual full astrologic operating model.

This document is not complete when it "looks good."
It is complete only when it is validated against the golden natal corpus.

## Acceptance Gate

This ontology is not accepted until:

- it is checked against at least 15 golden natal charts
- each promise domain has at least 2 chart-backed examples or is marked `v1_experimental`
- each contradiction type has at least 1 chart-backed example or is excluded from `v1`
- each evidence role has at least 1 chart-backed example

## Decision 1: Promise Domains

Status: provisional_v1

Purpose:

- provide the stable top-level domains that period, daily, synastry, and composite will later reference

Proposed domains:

- `identity`
- `emotional_security`
- `relationship`
- `money_self_worth`
- `communication_learning`
- `career_visibility`
- `home_family`
- `desire_conflict`
- `health_rhythm`
- `spiritual_meaning`
- `growth_shadow`

Notes:

- `health_rhythm` should stay conservative in `v1`; use rhythm/body/function language, not medical claims
- `desire_conflict` remains separate from `relationship` in `v1`
- `spiritual_meaning` should render in product language as direction, purpose, or higher meaning

## Decision 2: Character Pattern Types

Status: provisional_v1

Purpose:

- distinguish stable natal coping/expression architecture from promise themes

Proposed types:

- `temperament`
- `defense`
- `attachment_style`
- `expression_style`
- `ambition_style`
- `regulation_style`
- `visibility_style`

Notes:

- a character pattern explains how the person tends to live or defend a promise
- a promise is not automatically a pattern and should not collapse into trait language

## Decision 3: Contradiction Types

Status: provisional_v1

Purpose:

- define the bounded set of canonical natal polarity families for `v1`

Proposed types:

- `freedom_vs_belonging`
- `visibility_vs_privacy`
- `closeness_vs_threshold`
- `control_vs_surrender`
- `structure_vs_flow`
- `idealization_vs_reality`
- `independence_vs_dependency`

Notes:

- contradiction type names are internal; renderer wording may differ
- a contradiction is only canonical if the polarity is structurally repeated, not merely present once

## Decision 4: Evidence Roles

Status: provisional_v1

Purpose:

- normalize how chart facts function in canonical reasoning

Proposed roles:

- `root`
- `driver`
- `modifier`
- `support`
- `contradiction`
- `manifestation_channel`
- `governing_filter`

Notes:

- the same technical factor may support different roles in different nodes
- renderers may compress evidence language, but not delete the underlying role mapping

## Decision 5: Chart Spine Fields

Status: provisional_v1

Purpose:

- define the stable natal lines that future temporal systems can activate

Proposed fields:

- `primary_identity_line`
- `emotional_regulation_line`
- `relational_line`
- `work_visibility_line`
- `shadow_protection_line`
- `growth_integration_line`

Notes:

- these are canonical internal fields
- user-facing surfaces may rephrase them into product language

## Decision 6: V1 Technical Scope

Status: provisional_v1

In scope for `v1`:

- placidus houses
- chart ruler
- house rulers
- dispositor chains
- major aspects
- angular emphasis
- element and modality support
- dominant planets
- public/private polarity
- contradiction signatures
- promise vectors
- chart spine

Deferred or secondary for `v1.1+`:

- sect
- essential dignity as a stronger first-class axis
- profections
- progressed moon
- solar return
- lunar return
- advanced reception logic

Notes:

- modern psychological rulership is the default public model for `v1`
- traditional rulership remains available as internal support or debug signal

## Decision 7: User-Facing Technical Evidence Density

Status: provisional_v1

Public rendering guidance:

- compact surfaces: maximum 1 technical evidence phrase
- section surfaces: maximum 2 technical evidence phrases per section
- deeper reports may expose expandable evidence blocks

Notes:

- canonical state always stores technical evidence even when renderer hides it
- renderers may translate lightly, but not invent unsupported claims

## Decision 8: Legacy Branch Mapping Policy

Status: provisional_v1

Primary policy:

- old branch outputs are not canonical authorities
- old branch outputs are comparison, rescue, and renderer-inspiration inputs only

Initial role mapping:

- `dispositor_engine.py` -> `SOURCE_CALCULATOR`
- `natal_graph_v2.py` -> `STRUCTURAL_FEATURE_EXTRACTOR`
- `promise_vector_engine.py` -> `STRUCTURAL_FEATURE_EXTRACTOR`
- `natal_feature_graph.py` -> `STRUCTURAL_FEATURE_EXTRACTOR`
- `contradiction_engine.py` -> `STRUCTURAL_FEATURE_EXTRACTOR`
- `master_selector.py` -> `CANONICAL_REASONER_CANDIDATE_REDUCER`
- `sections_v2` -> `LEGACY_SURFACE`
- `supporting_threads` -> `LEGACY_SURFACE`
- `personality_imprint` -> `LEGACY_SURFACE`
- `profile_narrative` -> `LEGACY_SURFACE`
- `profile_v8` / `full_map_v8` -> `LEGACY_SURFACE`
- `public_builder.py` old branch-coordinator behavior -> `LEGACY_SURFACE`

## Open Validation Table

The following items still require chart-backed annotation during the golden corpus pass:

- promise domain examples
- contradiction type examples
- evidence role examples
- cases that should be marked `v1_experimental`

## Definition of Done

This sheet is complete when:

- all 8 decisions are frozen for `v1`
- the acceptance gate is satisfied
- unresolved ontology drift is recorded explicitly rather than hidden in renderer logic
