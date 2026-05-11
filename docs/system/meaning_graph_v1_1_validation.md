# meaning_graph_v1_1 Validation (Fresh Natal Public Payload)

Date: 2026-04-24  
Scope: One fresh `POST /interpret/ui` payload (natal), no code changes.

## How payload was generated
- Generated directly from backend route function:
  - `app.api.routes.natal_interpretation.interpret_natal_chart_ui(...)`
- Request used:
  - `birth_date=1996-12-28`
  - `birth_time=07:10`
  - `birth_place=Istanbul, TR`
  - `locale=tr`
  - `summary_only=false`

---

## 1) meaning_graph vs meaning_graph_v1_1

### 1.1 Structural comparison
| Metric | meaning_graph (v1) | meaning_graph_v1_1 |
|---|---:|---:|
| Node count | 51 | 51 |
| Evidence count | 67 | 189 |
| Source family coverage | 4/4 | 4/4 |
| Source families | core_story_ui, user_compact, personality_imprint, supporting_threads | core_story_ui, user_compact, personality_imprint, supporting_threads |

### 1.2 Layer distribution

#### v1 (single layer per node)
- recognition: 1
- mechanism: 3
- effect: 19
- shadow: 17
- potential: 8
- cause: 3

#### v1.1 (primary layer)
- recognition: 13
- mechanism: 5
- effect: 11
- shadow: 16
- potential: 6

#### v1.1 (all layers across `layers[]`)
- mechanism: 9
- shadow: 20
- effect: 17
- recognition: 15
- potential: 8

### 1.3 node_type distribution (v1.1)
- signal: 38
- guidance: 5
- reference: 4
- narrative: 4
- quality: 0

Observation: v1.1 is materially richer in evidence, but currently heavily skewed to `signal`.

---

## 2) Semantic fidelity check

## 2.1 Where v1.1 preserves nuance better than v1

1. Structured drivers are preserved as typed evidence (not string-only tags)
- v1: `core_story_ui.drivers[]` appears mainly as flattened tag strings.
- v1.1: same drivers are emitted as `structured_payload` with typed keys (`type/key/value`) under `kind=signal_driver`.

2. personality_imprint support metadata is retained
- v1: trait/shadow/gift summaries are present, but `support_keys`, `drive`, `background_hint` are weakly represented.
- v1.1: emits additional typed/text evidence from:
  - `support_keys` (`structured_payload`)
  - `drive` (text evidence)
  - `background_hint` (text/reference evidence)

3. supporting_threads proof signals are preserved
- v1: thread paragraph/body survives, but proof channels are not first-class semantic evidence.
- v1.1: retains `proof_raw` and `chips` as typed structured evidence (`reference` / `signal`).

4. Mixed sentence handling exists (vs forced single layer)
- v1 forces one layer per node.
- v1.1 supports `layers[]` and contrast-based 2-layer selection (e.g., `ama/ancak/but`).

## 2.2 Where v1.1 still loses nuance

1. No relations/groups
- `relations` and `groups` are intentionally absent.
- Consequence: no explicit causal/contrast graph links between nodes.

2. Some node_type misclassification remains
- Example: `core_story_ui.text` and long supporting thread paragraphs are classified as `reference` because text contains astro-like tokens (`3. ev`), despite being narrative meaning.
- Evidence: 4 long `reference` nodes (>120 chars), all semantic narrative text.

3. Layer misclassification still occurs in some entries
- Example mismatches from current fresh payload:
  - `Güneş 1. Ev Potential` -> primary layer `recognition` (expected `potential`)
  - `Venüs 12. Ev Shadow` -> primary layer `mechanism` (expected `shadow`)

4. Over-compression in node_type
- `signal` dominates (38/51), suggesting many multi-claim entries are still compressed to atomic typing.

---

## 3) Duplication inventory (v1.1 vs major branches)

Method: normalized text overlap (`equal` / containment) between `meaning_graph_v1_1.nodes[].summary` and branch text fields.

| Branch | Overlap snapshot | Classification | Notes |
|---|---|---|---|
| core_story_ui | 1 matched node / 6 branch text items | useful variant | Canonical source family; overlap expected and healthy. |
| user_compact | 5 matched nodes / 20 text items | useful variant + duplicate | Domain summaries map well; micro insights partially duplicate domain summaries. |
| personality_imprint | 42 matched nodes / 96 text items | useful variant | Strong direct semantic mapping (trait/shadow/gift). |
| supporting_threads | 3 matched nodes / 18 text items | useful variant | Paragraph-level mapping works; proof/chips now typed in v1.1 evidence. |
| profile_v8 | 1 matched node / 124 text items | render projection | Mostly projection surface; limited direct semantic source role. |
| profile_narrative | 9 matched nodes / 980 text items | duplicate + render projection | Re-renders personality/thread meaning; high overlap on detail-card bodies. |
| sections_v2 | 2 matched nodes / 36 text items | fallback-only (semantic) + possible dead branch | Current overlap mostly subtitle echoes from supporting_threads; low unique semantic contribution to v1.1. |

### Category examples
- useful variant: core source family text mirrored in graph intentionally.
- duplicate: user_compact micro-insight text repeated from domain summary.
- fallback-only: sections_v2 overlaps largely redundant to supporting_threads in this sample.
- render projection: profile_v8/profile_narrative mostly represent rendered views.
- possible dead branch: sections_v2 as independent semantic compute path (for canonical meaning graph) is a future pruning candidate if no unique semantic signal is required.

---

## 4) Compute-pruning candidates (report only, no removals)

## 4.1 Safe to keep
1. `meaning_graph` (v1) + `meaning_graph_v1_1` dual emission
- Reason: migration safety, backward compatibility.

2. Core source family outputs
- `core_story_ui`, `user_compact`, `personality_imprint`, `supporting_threads`
- Reason: currently required to build both v1 and v1.1 robustly.

## 4.2 Safe to make lazy (future optimization)
1. `profile_v8` / `full_map_v8` generation for non-profile consumers
- Reason: low direct semantic overlap with v1.1; heavy render projection role.

2. `profile_narrative` deep blocks (`detail_cards`/`extra_blocks`) on requests that only need semantic backbone
- Reason: overlap indicates substantial re-render duplication.

3. `sections_v2` as parallel semantic channel
- Reason: in this sample, low unique overlap vs supporting_threads.

## 4.3 Debug-only candidate
1. Existing debug-only narrative internals should remain debug-gated
- Example: internal matrices and migration debug branches under `include_debug` flow.
- Candidate direction: keep semantic diagnostics in debug path, not public default payload.

## 4.4 Future removal candidate (post-migration)
1. `meaning_graph` v1 (after v1.1 adoption stabilizes)
- Candidate only after consumers switch and parity checks pass.

2. Parallel semantic reconstruction paths in render packs
- Candidate: reduce duplicate semantic computation once graph-first projection is stable.

---

## 5) Key conclusion
- v1.1 improves semantic fidelity vs v1 mainly through:
  - typed structured evidence
  - multi-layer capability
  - richer evidence density
- v1.1 still needs next-step tuning in:
  - `node_type` calibration (avoid narrative text being typed as `reference`)
  - layer calibration for `Potential` / `Shadow` labeled entries
  - duplication collapse strategy beyond additive coexistence.
