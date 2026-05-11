# Projection Shadow Selection Policy Gap Audit

Date: 2026-04-26  
Scope: `backend/app/meaning/projection_shadow_v1_builder.py` vs `docs/system/shou_selection_ranking_policy.md`  
Constraint: audit only, no code changes.

## 1) Executive Verdict

`projection_shadow_v1_builder.py` is **deterministic and partially aligned** with the new unified selection/ranking policy, but it still uses a relatively simple selection model:
- sort by `priority` + layer weight
- preferred surface first
- optional one-pass domain diversity

Major policy pieces are still missing:
- multi-signal composite scoring (importance + emotional + uniqueness + domain + layer)
- semantic soft dedupe (`dedupe_fingerprint` + similarity)
- surface-specific layer/domain quotas and conflict rules
- full fallback ladder

Smallest safe migration slice: **augment `_pick_nodes` with policy scoring + hard/soft dedupe in graph-only scope**, while keeping all editorial text generation untouched.

## 2) Area-by-Area Audit

| area | current implementation evidence | policy target | alignment status | migration status | notes |
|---|---|---|---|---|---|
| 1. Current node sorting logic | `_sorted_nodes` sorts by `-_node_priority`, `-_top_layer_weight`, `node_id` ([projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:174)) | weighted composite score + tie-break rules ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:89)) | partially aligned | safe to migrate first | Deterministic tie-break exists; composite scoring missing. |
| 2. Current node picking logic | `_pick_nodes` = preferred-surface bucket then fallback bucket; truncation by limit ([projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:311)) | surface-specific selection counts + layer/domain conflict rules ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:109)) | partially aligned | safe to migrate first | Counts are hardcoded by caller; no policy-aware conflict resolution. |
| 3. Current domain diversity logic | `enforce_domain_diversity=True` enforces unique-domain first pass, then fills from remaining ([projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:333)) | per-surface max-per-domain and diversity targets ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:123)) | partially aligned | safe to migrate first | Current logic is binary (unique-first); policy needs richer caps/targets. |
| 4. Current surface filtering logic | Uses `projection_hints.surfaces` intersection with preferred sets ([projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:305), [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:320)) | surface-specific prioritization and slot intent per surface ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:129)) | partially aligned | safe to migrate first | Filtering exists, but no slot/layer intent orchestration. |
| 5. Current dedupe behavior | only node-id uniqueness inside `_pick_nodes`; no `dedupe_fingerprint`/similarity usage (absence confirmed) | hard dedupe by fingerprint + soft dedupe by similarity ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:206)) | missing | safe to migrate first | Biggest correctness gap for repeated semantic content. |
| 6. Current fallback behavior | implicit fallback inside `_pick_nodes` (preferred bucket then non-preferred); v8 has local fallback (`differentiator_nodes = nodes[:3]`) ([projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:329), [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:147)) | ordered fallback ladder (surface hints → diversity relaxation → layer quota relaxation → soft dedupe relaxation → legacy fallback) ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:223)) | partially aligned | risky to change now | Graph-only projection constraint makes legacy/source fallback risky in this builder. |
| 7. Current differences from unified policy | builder emits `profile_narrative_projection_v1` and `profile_v8_projection_v1` only; no Home/Story selection path in file ([projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:60), [projection_shadow_v1_builder.py](/Users/sahradenizozdogan/Astrologi-Ai/backend/app/meaning/projection_shadow_v1_builder.py:133)) | policy covers Home/Profile Top/Profile Cards/Profile Deep/Story ([shou_selection_ranking_policy.md](/Users/sahradenizozdogan/Astrologi-Ai/docs/system/shou_selection_ranking_policy.md:111)) | missing | risky to change now | Cross-surface orchestration belongs to higher orchestrator layer, not this projection-only builder. |

## 3) Detailed Gaps

## 3.1 Already aligned
- Deterministic ordering and tie-break stability:
  - Global node order is stable and deterministic (`priority`, layer weight, `node_id`).
- Preferred-surface-first behavior exists:
  - Nodes tagged for target surfaces are selected before others.
- Basic domain diversity exists:
  - One-pass unique-domain preference with deterministic fill.

## 3.2 Partially aligned
- Ranking signal coverage:
  - `importance_global` exists (via `projection_hints.priority`), but no explicit emotional/domain/layer weighting fusion.
- Selection policy shape:
  - Per-call limits exist (e.g., core=4, extra=6), but not mapped to policy-defined layer/domain quotas.
- Fallback:
  - Has local fallback order inside same node pool, but not the full policy ladder.

## 3.3 Missing
- Hard semantic dedupe using `dedupe_fingerprint`.
- Soft semantic dedupe using deterministic similarity threshold.
- Surface-specific scoring function with explicit weights.
- Layer quota checks (e.g., mechanism/shadow/potential minimums).
- Node-type balance guards for deep selections.
- Cross-surface variation logic (avoid same top slot collisions).

## 3.4 Risk hotspots
- Injecting legacy/source fallback directly into projection builder:
  - conflicts with graph-only projection constraint for this path.
- Adding full Home/Story policy inside this file:
  - scope creep; should live in surface orchestrator / consumer-level selector.
- Large changes in ranking formula without guardrails:
  - can regress editorial parity and voice quality.

## 4) Keep / Change / Defer

## 4.1 What to keep
- `_sorted_nodes` determinism pattern.
- Preferred-surface filtering scaffolding in `_pick_nodes`.
- Existing projection output structure and traceability fields.
- Editorial body generation pipeline (`_select_projection_body`, pattern injection, quality checks).

## 4.2 What to change first (smallest safe slice)
1. Add policy-aware scoring function inside projection selection (profile-focused only):
   - importance + emotional + domain + layer + uniqueness.
2. Add hard dedupe in selection pass:
   - block same `dedupe_fingerprint` duplicates.
3. Add soft dedupe in selection pass:
   - deterministic Jaccard on normalized summaries.
4. Add lightweight per-surface caps:
   - max-per-domain and minimal layer presence for profile selection sets.

## 4.3 What to defer
- Full policy rollout for Home/Story slot orchestration.
- Legacy/source fallback chain from projection builder.
- Cross-surface top-slot anti-collision (Home vs Profile Top) until a shared orchestrator controls both surfaces.
- Advanced node_type quota tuning until parity telemetry is available.

## 5) Exact Minimal Implementation Plan (No Code Yet)

## Phase A — scoring adapter in projection selector (safe)
1. Introduce internal helper (projection scope only):
   - `_policy_score_node(node, surface, selected_nodes)` with deterministic formula.
2. Extend `_pick_nodes` signature minimally:
   - optional `surface_policy_key` and `domain_cap`.
3. Keep current default behavior when policy args are not passed (backward-safe).

## Phase B — dedupe and diversity hardening (safe)
1. Hard dedupe:
   - skip candidate if `dedupe_fingerprint` already selected.
2. Soft dedupe:
   - skip candidate if normalized-summary Jaccard exceeds threshold.
3. Add one controlled relaxation step only when under-filled:
   - allow one near-duplicate.

## Phase C — profile-only quotas (moderate but bounded)
1. For `profile_narrative` core+extra selection:
   - enforce small layer coverage targets (mechanism/shadow/potential where available).
2. For `profile_v8` insight/differentiator lists:
   - apply domain cap and layer balancing before fallback `nodes[:3]`.

## Phase D — verification gates
1. Determinism check:
   - repeated run gives identical selected `node_id` order for same payload.
2. Coverage check:
   - no drop in node/evidence traceability ratio.
3. Quality check:
   - no regression in Phase 1.7 voice audit metrics.

## 6) Bottom Line

`projection_shadow_v1_builder.py` is a strong deterministic base, but only a subset of unified policy is currently implemented.  
The safest first migration is **selection-core only** (scoring + dedupe + light quotas) while preserving graph-only scope and leaving orchestration-wide policy features for upper layers.
