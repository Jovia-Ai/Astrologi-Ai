# SHOU Selection & Ranking Policy

Date: 2026-04-26  
Scope: deterministic selection/ranking layer between `meaning_graph_v1_1` and surface orchestration.  
Non-goal: no builder/schema changes in this phase.

## 1) Current State: What Already Exists

This repo already has selection/ranking logic, but it is fragmented.

### 1.1 Existing (confirmed)
- `backend/app/meaning/meaning_graph_v1_1_builder.py`
  - Computes node-level `projection_hints.priority` (deterministic).
  - Computes layer vector (`layers[]`) and `primary_layer`.
  - Emits `dedupe_fingerprint`.
- `backend/app/meaning/projection_shadow_v1_builder.py`
  - Sorts nodes by `priority`, then top layer weight, then `node_id`.
  - Supports preferred surface filtering and optional domain diversity.
  - Uses deterministic IDs and anti-repetition quality checks.
- `backend/app/natal/profile_v8_payload_builder.py`
  - Has explicit weighted scoring for section selection.
  - Has section caps and signature dedupe.
- `backend/app/natal/public_builder.py`
  - Has core/extra/detail caps and card dedupe for `profile_narrative`.

### 1.2 Gap
- There is no single cross-surface policy for selecting from `meaning_graph_v1_1` with shared scoring, dedupe, and fallback behavior.
- This document defines that missing unified policy.

## 2) Canonical Ranking Signals (Per Node)

Input node fields used:
- `node_id`
- `node_type`
- `domain`
- `layers[]` + `primary_layer`
- `projection_hints.priority`
- `projection_hints.surfaces[]`
- `dedupe_fingerprint`
- `summary`
- `evidence_ids[]`

All signals are normalized to `0.0..1.0`.

### 2.1 Signal Definitions

1. `importance_global`
- Source: `node.projection_hints.priority` if present.
- Fallback: `max(layer.weight)` from `layers[]`.

2. `emotional_weight`
- Weighted layer intensity:
  - `shadow: 1.00`
  - `potential: 0.95`
  - `effect: 0.88`
  - `cause: 0.82`
  - `mechanism: 0.78`
  - `recognition: 0.70`
- Formula:
  - `sum(layer.weight * emotional_multiplier[layer])`, clamped `0..1`.

3. `uniqueness`
- Starts at `1.0`.
- Penalized by similarity to already selected nodes on same surface:
  - hard duplicate (`dedupe_fingerprint` equal): `0.0`
  - near duplicate (`summary_similarity >= 0.72`): `-0.55`
  - same domain + same primary layer + `summary_similarity >= 0.55`: `-0.30`
- Final clamp `0..1`.

4. `domain_priority`
- Surface-specific domain score table (see section 4).
- If domain not listed: `0.45`.

5. `layer_priority`
- Surface-specific top-layer priority score (see section 4).
- If layer not listed: `0.40`.

### 2.2 Deterministic Similarity for Soft Dedup

`summary_similarity(a, b)`:
- normalize text (lowercase, punctuation-light, Turkish char fold)
- token set Jaccard similarity:
  - `|A ∩ B| / |A ∪ B|`

No embedding, no randomness.

## 3) Final Ranking Score

For each candidate node on a given surface:

`score = (w1 * importance_global) + (w2 * emotional_weight) + (w3 * uniqueness) + (w4 * domain_priority) + (w5 * layer_priority)`

### 3.1 Weights by Surface

| surface | w1 importance | w2 emotional | w3 uniqueness | w4 domain | w5 layer |
|---|---:|---:|---:|---:|---:|
| Home | 0.30 | 0.22 | 0.18 | 0.12 | 0.18 |
| Profile Top | 0.28 | 0.18 | 0.18 | 0.16 | 0.20 |
| Profile Cards | 0.24 | 0.22 | 0.20 | 0.18 | 0.16 |
| Profile Deep | 0.22 | 0.20 | 0.18 | 0.20 | 0.20 |
| Story | 0.26 | 0.20 | 0.18 | 0.12 | 0.24 |

### 3.2 Deterministic Tie-Break Order
1. higher `importance_global`
2. higher top layer weight
3. larger `len(evidence_ids)`
4. lexicographic `node_id` ascending

## 4) Surface Selection Rules

## 4.1 Home

- Node count: `4` (+ optional share surrogate slot from projection/source if needed).
- Prioritized layers: `effect > recognition > potential > mechanism > shadow > cause`.
- Domain priorities:
  - `identity: 1.00`
  - `relationships: 0.85`
  - `mind: 0.78`
  - `life_direction: 0.74`
  - `emotional: 0.68`
  - `career: 0.66`
  - `general: 0.62`
- Diversity:
  - first 3 slots must be unique domains when possible.
  - max 2 nodes from same domain overall.
- Conflict resolution:
  - if two candidates compete for same layer/domain, keep higher score and higher uniqueness.

## 4.2 Profile Top

- Node count: `4`.
- Prioritized layers: `recognition > effect > mechanism > potential > shadow > cause`.
- Domain priorities:
  - `identity: 1.00`
  - `mind: 0.82`
  - `relationships: 0.75`
  - `general: 0.70`
  - `life_direction: 0.66`
  - `emotional: 0.62`
  - `career: 0.58`
- Diversity:
  - at least 2 unique domains.
  - max 2 nodes from any domain.
- Conflict resolution:
  - prefer node with stronger `recognition/effect` component for top slot.

## 4.3 Profile Cards

- Node count: `8`.
- Prioritized layers: `mechanism > shadow > potential > effect > cause > recognition`.
- Domain priorities:
  - `identity: 0.90`
  - `relationships: 0.90`
  - `mind: 0.84`
  - `emotional: 0.82`
  - `life_direction: 0.78`
  - `career: 0.72`
  - `general: 0.66`
- Diversity:
  - target >= 4 unique domains when available.
  - max 2 nodes per domain before fallback relaxation.
- Layer balance targets:
  - at least 1 `shadow`
  - at least 1 `potential`
  - at least 1 `mechanism`
- Conflict resolution:
  - if quota conflict occurs, keep node that satisfies missing layer quota first.

## 4.4 Profile Deep

- Node count: `10`.
- Prioritized layers: `mechanism > cause > shadow > potential > effect > recognition`.
- Domain priorities:
  - `relationships: 0.92`
  - `identity: 0.90`
  - `emotional: 0.88`
  - `mind: 0.84`
  - `life_direction: 0.80`
  - `career: 0.76`
  - `general: 0.70`
- Diversity:
  - target >= 5 unique domains when available.
  - max 3 nodes per domain.
- Node type balance:
  - at least 2 `narrative`
  - max 3 `signal` in deep set
- Conflict resolution:
  - prefer deeper layer coverage (`cause/shadow/mechanism`) over duplicated `effect` lines.

## 4.5 Story

- Node count: `6`.
- Ordered slot intent (deterministic):
  1. `effect` or `recognition` hook
  2. `mechanism`
  3. `shadow`
  4. `potential`
  5. `context/caution` capable node (`cause` or `shadow`)
  6. shareable close (`effect` or `potential`)
- Layer priorities for scoring fallback: `effect > mechanism > shadow > potential > cause > recognition`.
- Diversity:
  - no adjacent slots from same domain unless pool is limited.
- Conflict resolution:
  - slot-fit wins over raw score when slot layer is missing.

## 5) Soft Dedup Policy

Dedup scope: per surface selection pass.

### 5.1 Hard Dedup
- If `dedupe_fingerprint` identical: keep first higher-scored node only.

### 5.2 Soft Dedup
- If near duplicate (`summary_similarity >= 0.72`), do not keep both on same surface.
- Exception:
  - allowed if primary layers differ and one is `shadow` while other is `potential` (intentional tension pair), and they are in different sequence slots.

### 5.3 Cross-Surface Variation
- Same node can appear on multiple surfaces.
- But avoid identical top positions across Home and Profile Top:
  - if same node already selected as Home slot-1, demote it below slot-1 in Profile Top when alternatives exist.

## 6) Fallback Rules

If surface cannot fill target count after strict rules:

1. Relax source surface hint constraint:
- allow nodes without matching `projection_hints.surfaces`.

2. Relax domain diversity:
- increase max-per-domain by +1.

3. Relax layer quotas:
- fill with next highest-scoring unique nodes.

4. Relax soft dedup once:
- allow one near-duplicate only if needed to meet minimum count.

5. Final fallback to existing source/projection branches:
- Home: `core_story_ui`, `user_compact`.
- Profile Top/Cards/Deep/Story: projection outputs first, then legacy packs.

All fallback steps are deterministic and ordered.

## 7) Deterministic Selection Procedure

1. Build candidate pool from `meaning_graph_v1_1.nodes`.
2. Pre-filter invalid nodes (`node_id`, `summary`, `layers` required).
3. Apply surface-specific preferred hint filter.
4. Score candidates with section 3 formula.
5. Select greedily with diversity + layer rules.
6. Apply hard/soft dedup.
7. Fill missing slots via fallback ladder (section 6).
8. Final stable sort by slot order then tie-break rules.

## 8) Implementation Notes (No Code Change Yet)

- This policy is designed to map directly to existing fields and deterministic utilities.
- It does not require schema changes.
- It does not introduce new meaning sources.
- It is compatible with current graph-first + projection-first orchestration.

## 9) Evidence Pointers

- Graph ranking primitives:
  - `backend/app/meaning/meaning_graph_v1_1_builder.py`
    - `_projection_priority`
    - `_infer_surfaces`
    - `_dedupe_fingerprint`
- Existing graph projection selection:
  - `backend/app/meaning/projection_shadow_v1_builder.py`
    - `_sorted_nodes`
    - `_pick_nodes`
- Legacy profile ranking:
  - `backend/app/natal/profile_v8_payload_builder.py`
    - `score_fragment_for_section`
    - `_rank_section_candidates`
    - `dedupe_selected_signatures`
- Legacy profile narrative caps/dedupe:
  - `backend/app/natal/public_builder.py`
    - `_build_profile_narrative_v3`
    - `_dedupe_profile_cards`
